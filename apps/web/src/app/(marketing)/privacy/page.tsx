import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Kebijakan Privasi - uReport AI",
};

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-8">Kebijakan Privasi</h1>
      <p className="text-muted-foreground mb-8">
        Terakhir diperbarui: Januari 2025
      </p>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">1. Informasi yang Kami Kumpulkan</h2>
        <p>Kami mengumpulkan informasi berikut saat Anda menggunakan layanan uReport AI:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>
            <strong>Data Akun:</strong> Nama, alamat email, dan kata sandi terenkripsi saat
            Anda mendaftar.
          </li>
          <li>
            <strong>File yang Diunggah:</strong> Dokumen dan file data yang Anda unggah untuk
            dianalisis oleh platform.
          </li>
          <li>
            <strong>Data Penggunaan:</strong> Informasi tentang bagaimana Anda berinteraksi
            dengan layanan, termasuk log aktivitas dan preferensi.
          </li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">2. Bagaimana Kami Menggunakan Informasi</h2>
        <p>Informasi yang kami kumpulkan digunakan untuk:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Menyediakan dan memelihara layanan analisis data dan pembuatan laporan.</li>
          <li>Meningkatkan kualitas dan performa platform.</li>
          <li>Mengirimkan notifikasi penting terkait layanan.</li>
          <li>Menyediakan dukungan teknis kepada pengguna.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">3. Penyimpanan Data</h2>
        <p>
          Data Anda disimpan dengan enkripsi pada server cloud yang aman. Kami menerapkan
          langkah-langkah keamanan teknis dan organisasi yang sesuai untuk melindungi data
          Anda dari akses tidak sah, perubahan, pengungkapan, atau penghancuran.
        </p>
        <p>
          File yang diunggah akan disimpan selama akun Anda aktif. Anda dapat menghapus file
          kapan saja melalui pengaturan akun. Setelah penghapusan akun, semua data akan
          dihapus dalam waktu 30 hari.
        </p>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">4. Layanan Pihak Ketiga</h2>
        <p>Kami menggunakan layanan pihak ketiga berikut:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>
            <strong>Penyedia Model AI (LLM):</strong> Untuk memproses permintaan analisis
            data. Data yang dikirim ke penyedia LLM diproses sesuai kebijakan privasi mereka.
          </li>
          <li>
            <strong>Layanan Analitik:</strong> Untuk memahami pola penggunaan dan
            meningkatkan layanan.
          </li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">5. Hak Pengguna</h2>
        <p>Anda memiliki hak untuk:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Mengakses data pribadi yang kami simpan tentang Anda.</li>
          <li>Meminta penghapusan data pribadi Anda.</li>
          <li>Mengekspor data Anda dalam format yang dapat dibaca mesin (portabilitas data).</li>
          <li>Menarik persetujuan pemrosesan data kapan saja.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">6. Keamanan</h2>
        <p>
          Kami menerapkan langkah-langkah keamanan berikut untuk melindungi data Anda:
        </p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Enkripsi data dalam transit (TLS/SSL) dan saat disimpan (at-rest encryption).</li>
          <li>Kontrol akses berbasis peran untuk staf internal.</li>
          <li>Audit keamanan berkala dan pemantauan sistem.</li>
          <li>Autentikasi dua faktor untuk akses administratif.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">7. Kontak</h2>
        <p>
          Jika Anda memiliki pertanyaan tentang kebijakan privasi ini, silakan hubungi kami
          melalui email di{" "}
          <a href="mailto:privacy@ureport.ai" className="text-primary hover:underline">
            privacy@ureport.ai
          </a>
          .
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">8. Perubahan Kebijakan</h2>
        <p>
          Kami dapat memperbarui kebijakan privasi ini dari waktu ke waktu. Perubahan
          signifikan akan diberitahukan melalui email atau notifikasi dalam aplikasi.
          Penggunaan layanan secara berkelanjutan setelah perubahan dianggap sebagai
          penerimaan terhadap kebijakan yang diperbarui.
        </p>
      </section>
    </div>
  );
}
