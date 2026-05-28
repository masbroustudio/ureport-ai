import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Syarat & Ketentuan - uReport AI",
};

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-8">Syarat & Ketentuan</h1>
      <p className="text-muted-foreground mb-8">
        Terakhir diperbarui: Januari 2025
      </p>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">1. Penerimaan Syarat</h2>
        <p>
          Dengan mengakses atau menggunakan layanan uReport AI, Anda menyetujui untuk
          terikat oleh syarat dan ketentuan ini. Jika Anda tidak menyetujui salah satu
          bagian dari syarat ini, Anda tidak diperkenankan menggunakan layanan kami.
        </p>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">2. Deskripsi Layanan</h2>
        <p>
          uReport AI adalah platform berbasis kecerdasan buatan yang menyediakan layanan
          analisis data dan pembuatan laporan terstruktur. Layanan ini mencakup:
        </p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Analisis data melalui antarmuka percakapan (chat).</li>
          <li>Pembuatan visualisasi dan grafik dari data pengguna.</li>
          <li>Generasi laporan dalam berbagai format.</li>
          <li>Penyimpanan dan pengelolaan basis pengetahuan.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">3. Akun Pengguna</h2>
        <p>
          Untuk menggunakan layanan, Anda harus mendaftarkan akun dengan informasi yang
          akurat dan lengkap. Anda bertanggung jawab untuk:
        </p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Menjaga kerahasiaan kata sandi akun Anda.</li>
          <li>Semua aktivitas yang terjadi di bawah akun Anda.</li>
          <li>Memberitahu kami segera jika terjadi penggunaan tidak sah.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">4. Penggunaan yang Diperbolehkan</h2>
        <p>Anda setuju untuk tidak menggunakan layanan untuk:</p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Tujuan ilegal atau tidak sah.</li>
          <li>Mengunggah konten yang melanggar hak kekayaan intelektual pihak lain.</li>
          <li>Mendistribusikan malware atau kode berbahaya.</li>
          <li>Mencoba mengakses sistem atau data tanpa otorisasi.</li>
          <li>Menggunakan layanan untuk membuat konten yang menyesatkan atau berbahaya.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">5. Konten Pengguna</h2>
        <p>
          Anda mempertahankan kepemilikan atas semua data dan konten yang Anda unggah ke
          platform. Dengan mengunggah konten, Anda memberikan kami lisensi terbatas untuk
          memproses, menganalisis, dan menyimpan konten tersebut sesuai kebutuhan layanan.
        </p>
        <p>
          Kami tidak akan menggunakan konten Anda untuk tujuan lain tanpa persetujuan
          eksplisit dari Anda.
        </p>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">6. Hak Kekayaan Intelektual</h2>
        <p>
          Platform uReport AI, termasuk desain, kode sumber, algoritma, dan dokumentasi,
          dilindungi oleh hak cipta dan hukum kekayaan intelektual yang berlaku. Anda tidak
          diperkenankan untuk menyalin, memodifikasi, mendistribusikan, atau membuat karya
          turunan dari platform tanpa izin tertulis.
        </p>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">7. Batasan Tanggung Jawab</h2>
        <p>
          Layanan disediakan &quot;sebagaimana adanya&quot; tanpa jaminan dalam bentuk apa
          pun. Kami tidak bertanggung jawab atas:
        </p>
        <ul className="list-disc pl-6 space-y-2">
          <li>Ketidakakuratan hasil analisis yang dihasilkan oleh AI.</li>
          <li>Kerugian yang timbul dari penggunaan atau ketidakmampuan menggunakan layanan.</li>
          <li>Kehilangan data akibat kegagalan sistem di luar kendali kami.</li>
          <li>Gangguan layanan karena pemeliharaan atau force majeure.</li>
        </ul>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">8. Penghentian Layanan</h2>
        <p>
          Kami berhak menghentikan atau menangguhkan akses Anda ke layanan kapan saja, dengan
          atau tanpa pemberitahuan, jika Anda melanggar syarat dan ketentuan ini. Anda juga
          dapat menghentikan akun Anda kapan saja melalui pengaturan akun.
        </p>
      </section>

      <section className="space-y-4 mb-8">
        <h2 className="text-xl font-semibold">9. Perubahan Syarat</h2>
        <p>
          Kami berhak mengubah syarat dan ketentuan ini kapan saja. Perubahan akan berlaku
          segera setelah dipublikasikan di platform. Penggunaan layanan secara berkelanjutan
          setelah perubahan dianggap sebagai penerimaan syarat yang diperbarui.
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold">10. Hukum yang Berlaku</h2>
        <p>
          Syarat dan ketentuan ini diatur oleh dan ditafsirkan sesuai dengan hukum yang
          berlaku di Republik Indonesia. Setiap sengketa yang timbul akan diselesaikan
          melalui musyawarah terlebih dahulu, dan jika tidak tercapai kesepakatan, akan
          diselesaikan melalui pengadilan yang berwenang di Indonesia.
        </p>
      </section>
    </div>
  );
}
