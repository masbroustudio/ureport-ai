import asyncio
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.prompts import build_data_analysis_system_prompt, extract_code_from_response
from app.data.sandbox import SandboxExecutor
from app.deps import get_current_user, get_db
from app.llm.client import stream_chat_completion
from app.llm.router import get_default_model
from app.model.conversation import Conversation
from app.model.file import File
from app.model.message import Message
from app.model.usage_log import UsageLog
from app.model.user import User
from app.rag.retriever import retrieve
from app.schema.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
)
from app.service.files import get_full_path
from app.settings import settings

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(
    cursor: str | None = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )

    if cursor:
        cursor_dt = datetime.fromisoformat(cursor)
        query = query.where(Conversation.updated_at < cursor_dt)

    result = await db.execute(query)
    conversations = result.scalars().all()
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    model_str = request.model or get_default_model(settings)
    provider = model_str.split("/")[0] if "/" in model_str else None
    model_name = model_str.split("/", 1)[1] if "/" in model_str else model_str

    conversation = Conversation(
        user_id=current_user.id,
        title=request.title,
        model_provider=provider,
        model_name=model_name,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return ConversationResponse.model_validate(conversation)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID,
    request: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)

    await db.commit()
    await db.refresh(conversation)
    return ConversationResponse.model_validate(conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: uuid.UUID,
    cursor: str | None = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify conversation ownership
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )

    if cursor:
        cursor_dt = datetime.fromisoformat(cursor)
        query = query.where(Message.created_at > cursor_dt)

    result = await db.execute(query)
    messages = result.scalars().all()
    return [MessageResponse.model_validate(m) for m in messages]


@router.post("/{conversation_id}/messages")
async def create_message(
    conversation_id: uuid.UUID,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify conversation ownership
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.content,
        status="done",
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Build message history (limit to last 50 messages to prevent exceeding context limits)
    MAX_HISTORY_MESSAGES = 50
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    )
    history = list(reversed(history_result.scalars().all()))
    messages_for_llm = [{"role": m.role, "content": m.content} for m in history if m.content]

    # If file_ids provided, load profiles and prepend data analysis system prompt
    file_records = []
    if request.file_ids:
        file_result = await db.execute(
            select(File).where(
                File.id.in_([uuid.UUID(fid) for fid in request.file_ids]),
                File.user_id == current_user.id,
            )
        )
        file_records = list(file_result.scalars().all())

        if file_records:
            # Use the first file's profile for system prompt
            for fr in file_records:
                if fr.profile_json:
                    system_prompt = build_data_analysis_system_prompt(fr.profile_json)
                    messages_for_llm.insert(0, {"role": "system", "content": system_prompt})
                    break

    # RAG: If kb_document_ids provided, retrieve relevant chunks and add context
    rag_results = []
    if request.kb_document_ids:
        rag_results = await retrieve(
            user_id=str(current_user.id),
            query=request.content,
            document_ids=request.kb_document_ids,
        )
        if rag_results:
            rag_context_parts = [
                "Use the following knowledge base context to answer. "
                "Cite sources using [^N] notation.\n"
            ]
            for i, result in enumerate(rag_results):
                source_info = f"Source: {result.document_name}"
                if result.page:
                    source_info += f", Page {result.page}"
                rag_context_parts.append(
                    f"[^{i + 1}] {source_info}\n{result.text}"
                )
            rag_system_msg = "\n\n".join(rag_context_parts)
            messages_for_llm.insert(0, {"role": "system", "content": rag_system_msg})

    # Determine model
    model = request.model
    if not model:
        provider = conversation.model_provider or ""
        name = conversation.model_name or ""
        model = f"{provider}/{name}" if provider else get_default_model(settings)

    async def event_stream():
        accumulated_text = ""
        usage_info = None

        try:
            async for chunk in stream_chat_completion(messages_for_llm, model, settings):
                if chunk["type"] == "token":
                    accumulated_text += chunk["text"]
                    event_data = json.dumps({"text": chunk["text"]})
                    yield f"event: token\ndata: {event_data}\n\n"
                elif chunk["type"] == "done":
                    usage_info = chunk.get("usage")

            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=accumulated_text,
                status="done",
                model=model,
                tokens_in=usage_info.get("tokens_in") if usage_info else None,
                tokens_out=usage_info.get("tokens_out") if usage_info else None,
            )
            db.add(assistant_message)

            # Log usage
            usage_log = UsageLog(
                user_id=current_user.id,
                provider=model.split("/")[0] if "/" in model else None,
                model=model,
                tokens_in=usage_info.get("tokens_in") if usage_info else None,
                tokens_out=usage_info.get("tokens_out") if usage_info else None,
                task_type="chat",
                conversation_id=conversation_id,
            )
            db.add(usage_log)
            await db.commit()
            await db.refresh(assistant_message)

            # If files are attached, check for code in response and execute
            # This must happen BEFORE the done event so clients receive results
            if file_records and accumulated_text:
                code = extract_code_from_response(accumulated_text)
                if code:
                    yield f"event: code\ndata: {json.dumps({'code': code})}\n\n"

                    # Execute code against the first file
                    target_file = file_records[0]
                    full_path = get_full_path(target_file.storage_path, settings)
                    executor = SandboxExecutor(
                        timeout=settings.DATA_SANDBOX_TIMEOUT_SECONDS
                    )
                    exec_result = await asyncio.to_thread(
                        executor.execute, code, full_path, target_file.mime
                    )

                    if exec_result.chart_spec:
                        yield f"event: chart\ndata: {json.dumps(exec_result.chart_spec, default=str)}\n\n"
                    if exec_result.table_data:
                        table_payload = {
                            "columns": list(exec_result.table_data[0].keys()) if exec_result.table_data else [],
                            "rows": exec_result.table_data,
                        }
                        yield f"event: table\ndata: {json.dumps(table_payload, default=str)}\n\n"
                    if exec_result.error:
                        yield f"event: error\ndata: {json.dumps({'detail': exec_result.error})}\n\n"

            done_data = json.dumps({
                "message_id": str(assistant_message.id),
                "usage": usage_info,
            })

            # Emit citation events for RAG results before done
            if rag_results:
                for i, result in enumerate(rag_results):
                    citation_data = json.dumps({
                        "id": str(i + 1),
                        "doc_name": result.document_name,
                        "page": result.page,
                        "text": result.text[:200],
                        "section": result.section,
                    })
                    yield f"event: citation\ndata: {citation_data}\n\n"

            yield f"event: done\ndata: {done_data}\n\n"

        except Exception as e:
            # Persist partial assistant message if any text was accumulated
            if accumulated_text:
                partial_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=accumulated_text,
                    status="error",
                    model=model,
                )
                db.add(partial_message)
                try:
                    await db.commit()
                except Exception:
                    pass
            error_data = json.dumps({"detail": str(e)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
