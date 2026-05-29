"use client";

import React, { useState, useRef, useEffect } from "react";
import Image from "next/image";
import { useInView } from "./hooks/useInView";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [heroLoaded, setHeroLoaded] = useState(false);

  const analyzeRef = useRef<HTMLDivElement>(null);
  const { ref: whyRef, isVisible: whyVisible } = useInView();
  const { ref: howRef, isVisible: howVisible } = useInView();
  const { ref: uploadRef, isVisible: uploadVisible } = useInView({ threshold: 0.1 });
  const { ref: disclaimerRef, isVisible: disclaimerVisible } = useInView({ threshold: 0.2 });
  const { ref: footerRef, isVisible: footerVisible } = useInView({ threshold: 0.1 });

  // Trigger hero entrance animation after mount
  useEffect(() => {
    const t = setTimeout(() => setHeroLoaded(true), 80);
    return () => clearTimeout(t);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Gagal menganalisis audio. Pastikan file valid dan coba lagi.");
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Terjadi kesalahan.");
    } finally {
      setLoading(false);
    }
  };

  const scrollToAnalyze = () => {
    analyzeRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-800">
      
      {/* ─────────────────────────────────────────
      SECTION 1 — HERO
      ───────────────────────────────────────── */}
      <section className="relative w-full h-screen min-h-[600px] flex items-center bg-[#08101e] overflow-hidden">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: "url('/assets/hero.webp')" }}
        />
        {/* Dark Overlay Gradient (Darker on the right) */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#04081833] via-[#040818ad] to-[#040818fa]" />

        <div className="relative z-10 w-full max-w-7xl mx-auto px-6 lg:px-8 flex justify-center text-center">
          <div className={`max-w-3xl pt-10 flex flex-col items-center ${heroLoaded ? "hero-loaded" : ""}`}>
            <div className="hero-enter hero-enter-delay-1 flex items-center justify-center gap-4 mb-6">
              <div className="w-8 h-[2px] bg-blue-300/70 rounded-full hidden sm:block"></div>
              <span className="font-montserrat text-[0.7rem] font-bold tracking-[0.28em] uppercase text-blue-200/90">
                Forensik Akustik Berbasis Kecerdasan Buatan
              </span>
              <div className="w-8 h-[2px] bg-blue-300/70 rounded-full hidden sm:block"></div>
            </div>
            
            <h1 className="hero-enter hero-enter-delay-2 font-sans text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold leading-[1.1] tracking-tight text-white mb-6">
              AI Deteksi Voice Cloning & Deepfake Bahasa Indonesia
            </h1>
            
            <p className="hero-enter hero-enter-delay-3 text-[1rem] font-light leading-relaxed text-slate-300 mb-10 max-w-2xl mx-auto">
              Analisis keaslian rekaman suara secara instan. Sistem AI kami mengidentifikasi 
              jejak forensik akustik dari algoritma Text-to-Speech untuk membedakan suara manusia asli dan sintetik.
            </p>
            
            <button 
              onClick={scrollToAnalyze}
              className="hero-enter hero-enter-delay-4 inline-block px-10 py-4 bg-blue-600 hover:bg-blue-700 text-white font-montserrat text-sm font-bold tracking-[0.1em] uppercase rounded-lg shadow-[0_6px_28px_rgba(37,99,235,0.45)] hover:shadow-[0_10px_36px_rgba(37,99,235,0.58)] hover:-translate-y-1 transition-all duration-300"
            >
              Mulai Analisis Audio
            </button>
          </div>
        </div>

        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center">
          <div className="w-[1px] h-[40px] bg-white/20 mb-3"></div>
          <svg
            className="w-5 h-5 text-white/30 animate-bounce"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path d="M3 6l5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      </section>

      {/* ─────────────────────────────────────────
      SECTION 2 — THE PROBLEM
      ───────────────────────────────────────── */}
      <section ref={whyRef as React.RefObject<HTMLDivElement>} className="py-24 px-6 lg:px-8 max-w-7xl mx-auto">

        {/* Section header */}
        <div className={`reveal reveal-fade ${whyVisible ? "reveal-visible" : ""} mb-16`}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-blue-600 rounded-full" />
            <span className="font-montserrat text-xs font-bold tracking-[0.22em] uppercase text-blue-600">
              Mengapa Ini Penting
            </span>
          </div>
          <h2 className="font-montserrat text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">
            Ancaman Nyata di Balik Suara Digital
          </h2>
          <p className="text-slate-500 max-w-2xl leading-relaxed text-[0.95rem]">
            Teknologi Voice Cloning telah berkembang pesat. Suara sintetik yang dihasilkan kini hampir
            tidak dapat dibedakan oleh telinga manusia biasa, menciptakan risiko serius di berbagai bidang.
          </p>
        </div>

        {/* Row 1: Dominant card + stat callout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">

          {/* Dominant card — col-span-7 */}
          <div className={`reveal ${whyVisible ? "reveal-visible" : ""} reveal-delay-1
            lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-10
            relative overflow-hidden group hover:border-blue-200 hover:shadow-lg transition-all duration-300`}>
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-red-500 to-orange-400" />
            <span className="font-montserrat text-[0.65rem] font-bold tracking-[0.22em] uppercase
              text-red-600 bg-red-50 px-3 py-1 rounded-full inline-block mb-6">
              Ancaman Kriminal
            </span>
            <h3 className="font-montserrat text-2xl font-extrabold text-slate-900 mb-4 leading-tight">
              Penipuan Finansial Berbasis Kloning Suara
            </h3>
            <p className="text-slate-500 leading-relaxed text-sm">
              Pelaku kejahatan menggunakan kloning suara anggota keluarga atau eksekutif perusahaan
              untuk meyakinkan korban agar melakukan transfer dana dalam jumlah besar.
              Serangan ini sulit dideteksi karena suara yang dihasilkan terdengar identik dengan aslinya.
            </p>
          </div>

          {/* Stat callout — col-span-5 */}
          <div className={`reveal ${whyVisible ? "reveal-visible" : ""} reveal-delay-2
            lg:col-span-5 bg-[#08101e] rounded-2xl p-10 flex flex-col justify-center`}>
            <div className="font-montserrat text-[0.65rem] font-bold tracking-[0.22em] uppercase
              text-blue-400 mb-4">
              Skala Ancaman Global
            </div>
            <div className="font-montserrat text-5xl font-black text-white leading-none mb-3">
              $25 M
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              Kerugian akibat penipuan berbasis kloning suara yang dilaporkan dalam satu insiden
              tunggal pada 2024 — angka yang terus meningkat setiap tahunnya.
            </p>
          </div>
        </div>

        {/* Row 2: Two compact cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          <div className={`reveal ${whyVisible ? "reveal-visible" : ""} reveal-delay-2
            bg-white border border-slate-200 rounded-2xl p-8
            relative overflow-hidden hover:border-blue-200 hover:shadow-lg transition-all duration-300`}>
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-amber-500 to-yellow-400" />
            <span className="font-montserrat text-[0.65rem] font-bold tracking-[0.22em] uppercase
              text-amber-700 bg-amber-50 px-3 py-1 rounded-full inline-block mb-5">
              Ancaman Demokrasi
            </span>
            <h3 className="font-montserrat text-lg font-bold text-slate-900 mb-3">
              Penyebaran Disinformasi
            </h3>
            <p className="text-sm text-slate-500 leading-relaxed">
              Tokoh publik sering menjadi korban manipulasi audio deepfake untuk menggiring opini publik,
              merusak reputasi, atau memprovokasi perpecahan sosial.
            </p>
          </div>

          <div className={`reveal ${whyVisible ? "reveal-visible" : ""} reveal-delay-3
            bg-white border border-slate-200 rounded-2xl p-8
            relative overflow-hidden hover:border-blue-200 hover:shadow-lg transition-all duration-300`}>
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-blue-600 to-cyan-400" />
            <span className="font-montserrat text-[0.65rem] font-bold tracking-[0.22em] uppercase
              text-blue-700 bg-blue-50 px-3 py-1 rounded-full inline-block mb-5">
              Solusi Teknologi
            </span>
            <h3 className="font-montserrat text-lg font-bold text-slate-900 mb-3">
              Keterbatasan Persepsi Manusia
            </h3>
            <p className="text-sm text-slate-500 leading-relaxed">
              Algoritma TTS modern menghasilkan suara berkualitas tinggi yang tidak lagi dapat dibedakan
              secara auditif. Diperlukan AI forensik untuk mendeteksinya secara andal.
            </p>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────
      SECTION 3 — HOW IT WORKS
      ───────────────────────────────────────── */}
      <section className="py-24 bg-white border-y border-slate-100">
        <div ref={howRef as React.RefObject<HTMLDivElement>} className="max-w-7xl mx-auto px-6 lg:px-8">

          {/* Section header */}
          <div className={`reveal reveal-fade ${howVisible ? "reveal-visible" : ""} mb-20`}>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-[2px] bg-blue-600 rounded-full" />
              <span className="font-montserrat text-xs font-bold tracking-[0.22em] uppercase text-blue-600">
                Cara Kerja Sistem
              </span>
            </div>
            <h2 className="font-montserrat text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">
              Tiga Tahap Analisis Forensik
            </h2>
            <p className="text-slate-500 max-w-2xl leading-relaxed text-[0.95rem]">
              Proses analisis berlangsung sepenuhnya otomatis melalui tiga tahap yang menggabungkan
              pemrosesan sinyal suara dan algoritma Deep Learning tingkat lanjut.
            </p>
          </div>

          {/* Two-column: steps left, image right */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-end">

            {/* Left — steps */}
            <div className="lg:col-span-2">
              {[
                {
                  num: "01",
                  title: "Unggah Audio",
                  body: "Masukkan file rekaman suara. Sistem menerima berbagai format dan durasi tanpa batasan panjang rekaman.",
                  tag: ".wav / .mp3 / .ogg",
                  delay: "reveal-delay-1",
                },
                {
                  num: "02",
                  title: "Ekstraksi Sidik Jari Akustik",
                  body: "Sistem menghilangkan jeda hening pada rekaman, lalu memindai spektrum frekuensi untuk mengekstrak representasi MFCC — sidik jari akustik yang unik untuk setiap sumber suara.",
                  tag: "Pemrosesan Sinyal Suara",
                  delay: "reveal-delay-2",
                },
                {
                  num: "03",
                  title: "Analisis Deep Learning",
                  body: "Model CNN meneliti pola sidik jari audio untuk menyimpulkan apakah suara tersebut berasal dari pita suara manusia atau dihasilkan oleh generator Text-to-Speech.",
                  tag: "Prediksi Berbasis AI",
                  delay: "reveal-delay-3",
                },
              ].map((step, i, arr) => (
                <div
                  key={step.num}
                  className={`reveal ${howVisible ? "reveal-visible" : ""} ${step.delay} flex gap-8`}
                >
                  {/* Step number + vertical connector */}
                  <div className="flex flex-col items-center">
                    <div className="w-12 h-12 rounded-full border-2 border-blue-600 text-blue-600
                      font-montserrat text-sm font-black flex items-center justify-center flex-shrink-0">
                      {step.num}
                    </div>
                    {i < arr.length - 1 && (
                      <div className="w-[2px] flex-1 bg-slate-200 my-3 min-h-[48px]" />
                    )}
                  </div>

                  {/* Step content */}
                  <div className="pb-12">
                    <h3 className="font-montserrat text-xl font-bold text-slate-900 mb-3 leading-tight">
                      {step.title}
                    </h3>
                    <p className="text-sm text-slate-500 leading-relaxed mb-4">
                      {step.body}
                    </p>
                    <code className="px-3 py-1.5 bg-slate-100 text-slate-600 text-xs font-mono rounded-md">
                      {step.tag}
                    </code>
                  </div>
                </div>
              ))}
            </div>

            {/* Right — AI illustration */}
            <div className={`reveal ${howVisible ? "reveal-visible" : ""} reveal-delay-2
              lg:col-span-3 hidden lg:flex items-end justify-center`}>
              <div className="relative w-full flex items-end justify-center">
                {/* Audio wave — background layer */}
                <Image
                  src="/assets/audio-wave.webp"
                  alt=""
                  width={800}
                  height={300}
                  aria-hidden="true"
                  className="absolute bottom-1/3 w-full h-auto object-contain opacity-30"
                  priority={false}
                />
                {/* AI robot — full size, no scale */}
                <Image
                  src="/assets/ai-photo-standing.webp"
                  alt="Ilustrasi AI forensik suara"
                  width={900}
                  height={900}
                  className="relative w-full h-auto"
                  priority={false}
                />
                {/* Subtle fade at very bottom only */}
                <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent pointer-events-none" />
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────
      SECTION 4 — CORE APP (UPLOAD)
      ───────────────────────────────────────── */}
      <section ref={analyzeRef} className="py-24 px-6 lg:px-8 max-w-4xl mx-auto">
        <div ref={uploadRef as React.RefObject<HTMLDivElement>}>
          <div className={`reveal reveal-fade ${uploadVisible ? "reveal-visible" : ""} text-center mb-12`}>
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="w-8 h-[2px] bg-blue-600 rounded-full"></div>
              <span className="font-montserrat text-xs font-bold tracking-[0.22em] uppercase text-blue-600">
                Analisis Audio
              </span>
              <div className="w-8 h-[2px] bg-blue-600 rounded-full"></div>
            </div>
            <h2 className="font-montserrat text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">
              Unggah dan Deteksi Sekarang
            </h2>
            <p className="text-slate-500">
              Unggah file rekaman suara dan sistem akan menganalisis keasliannya
              menggunakan forensik akustik berbasis AI.
            </p>
          </div>

          <div className={`reveal ${uploadVisible ? "reveal-visible" : ""} reveal-delay-1 bg-white p-8 md:p-12 rounded-2xl shadow-xl border border-slate-100 mb-12`}>
          <div className="border-2 border-dashed border-slate-300 hover:border-blue-400 bg-slate-50 hover:bg-blue-50 transition-colors rounded-xl p-10 text-center flex flex-col items-center justify-center">
            <input 
              type="file" 
              accept=".wav,.mp3,.ogg,.flac,.m4a"
              onChange={handleFileChange}
              className="mb-4 text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
            />
            {file && (
              <p className="text-sm font-medium text-slate-700 mt-2">
                Terpilih: {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full mt-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-montserrat text-sm font-bold tracking-[0.1em] uppercase rounded-lg shadow-lg transition-all duration-300 flex justify-center items-center gap-3"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Menganalisis Forensik...
              </>
            ) : "Mulai Deteksi"}
          </button>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              <span className="font-bold">Error:</span> {error}
            </div>
          )}
        </div>
        </div>{/* end uploadRef wrapper */}

        {/* ─────────────────────────────────────────
        RESULTS
        ───────────────────────────────────────── */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
            {/* Verdict Card */}
            <div className={`p-8 md:p-10 text-center rounded-2xl border-2 mb-10 ${
              result.prediction.is_fake 
                ? 'bg-red-50 border-red-200' 
                : 'bg-green-50 border-green-200'
            }`}>
              <div className={`font-montserrat text-[0.7rem] font-bold tracking-[0.2em] uppercase mb-2 ${
                result.prediction.is_fake ? 'text-red-700' : 'text-green-700'
              }`}>
                Hasil Analisis Forensik
              </div>
              
              <h3 className={`font-montserrat text-5xl md:text-6xl font-black tracking-tight mb-2 ${
                result.prediction.is_fake ? 'text-red-800' : 'text-green-800'
              }`}>
                {result.prediction.is_fake ? "PALSU (SINTETIK)" : "ASLI (MANUSIA)"}
              </h3>
              
              <div className={`font-mono text-xl md:text-2xl font-bold mb-6 ${
                result.prediction.is_fake ? 'text-red-600' : 'text-green-600'
              }`}>
                Confidence: {(result.prediction.confidence * 100).toFixed(1)}%
              </div>

              {/* Confidence Bar */}
              <div className="max-w-sm mx-auto h-2 bg-slate-200 rounded-full overflow-hidden mb-8">
                <div 
                  className={`h-full ${result.prediction.is_fake ? 'bg-red-500' : 'bg-green-500'}`}
                  style={{ width: `${result.prediction.confidence * 100}%` }}
                ></div>
              </div>

              {/* Breakdown */}
              <div className="flex justify-center gap-8 md:gap-16">
                <div>
                  <div className={`font-mono text-3xl font-bold ${result.prediction.is_fake ? 'text-red-600' : 'text-green-600'}`}>{result.prediction.fake_votes}</div>
                  <div className="font-montserrat text-[0.6rem] font-bold text-slate-500 uppercase tracking-widest mt-1">Segmen Palsu</div>
                </div>
                <div>
                  <div className="font-mono text-3xl font-bold text-slate-400">{result.prediction.total_chunks}</div>
                  <div className="font-montserrat text-[0.6rem] font-bold text-slate-500 uppercase tracking-widest mt-1">Total Segmen</div>
                </div>
                <div>
                  <div className={`font-mono text-3xl font-bold ${result.prediction.is_fake ? 'text-slate-400' : 'text-green-600'}`}>{result.prediction.real_votes}</div>
                  <div className="font-montserrat text-[0.6rem] font-bold text-slate-500 uppercase tracking-widest mt-1">Segmen Asli</div>
                </div>
              </div>
            </div>

            {/* Explainable AI Explain Box */}
            <div className="bg-slate-100 border-l-4 border-blue-600 rounded-r-lg p-6 mb-12">
              <h4 className="font-montserrat text-xs font-bold text-blue-700 uppercase tracking-wider mb-2">Penjelasan Sistem</h4>
              <p className="text-sm text-slate-700 leading-relaxed">
                {result.prediction.is_fake 
                  ? `Sistem AI mendeteksi kejanggalan pada rekaman ini. Dari total ${result.prediction.total_chunks} bagian suara yang dianalisis, sebanyak ${result.prediction.fake_votes} bagian (${(result.prediction.fake_votes/result.prediction.total_chunks*100).toFixed(0)}%) menunjukkan indikasi kuat buatan mesin. Pola gelombang suara menunjukkan keteraturan yang terlalu sempurna dan tidak alami — yang merupakan ciri khas dari suara hasil generator Deepfake.`
                  : `Tidak ditemukan kejanggalan yang berarti pada rekaman ini. Pola frekuensi dan variasi gelombang suaranya bersifat organik dan alami — sangat selaras dengan karakteristik pita suara manusia pada umumnya.`}
              </p>
            </div>

            {/* Plots */}
            <div className="space-y-8">
              <div>
                <h4 className="font-montserrat text-xs font-bold text-slate-500 uppercase tracking-widest border-b border-slate-200 pb-2 mb-4">
                  Visualisasi Aktivitas Sinyal Suara
                </h4>
                <img 
                  src={`data:image/png;base64,${result.plots.vad}`} 
                  alt="VAD Plot" 
                  className="w-full rounded-xl border border-slate-200 shadow-sm"
                />
              </div>
              
              <div>
                <h4 className="font-montserrat text-xs font-bold text-slate-500 uppercase tracking-widest border-b border-slate-200 pb-2 mb-4">
                  Peta Panas (Heatmap) Sidik Jari Audio
                </h4>
                <img 
                  src={`data:image/png;base64,${result.plots.mfcc_heatmap}`} 
                  alt="MFCC Heatmap" 
                  className="w-full rounded-xl border border-slate-200 shadow-sm"
                />
              </div>
              
              <div>
                <h4 className="font-montserrat text-xs font-bold text-slate-500 uppercase tracking-widest border-b border-slate-200 pb-2 mb-4">
                  Analisis Variasi Spektrum Frekuensi
                </h4>
                <img 
                  src={`data:image/png;base64,${result.plots.mfcc_variance}`} 
                  alt="MFCC Variance" 
                  className="w-full rounded-xl border border-slate-200 shadow-sm"
                />
              </div>
            </div>
          </div>
        )}
      </section>

      {/* ─────────────────────────────────────────
      SECTION 5 — DISCLAIMER
      ───────────────────────────────────────── */}
      <section className="py-16 bg-amber-50/50 border-t border-amber-100">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <div
            ref={disclaimerRef as React.RefObject<HTMLDivElement>}
            className={`reveal ${disclaimerVisible ? "reveal-visible" : ""} bg-amber-100/50 border border-amber-200 rounded-2xl p-8 md:p-10`}
          >
            <h4 className="font-montserrat text-xs font-bold text-amber-800 uppercase tracking-widest mb-4">
              Pernyataan Lingkup & Batasan
            </h4>
            <p className="text-sm text-amber-900 leading-relaxed mb-6">
              Sistem ini merupakan purwarupa algoritma Deep Learning tingkat lanjut yang dirancang khusus 
              untuk mendeteksi audio hasil kloning (generator suara berbasis AI). Model ini telah melalui proses pelatihan 
              dengan keandalan tinggi dan akurasi yang terukur.
            </p>
            <div className="flex flex-wrap gap-3">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-green-100 border border-green-200 text-green-800 rounded-full font-montserrat text-[0.65rem] font-bold tracking-wider uppercase">
                <svg className="w-3 h-3 flex-shrink-0" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Mendukung Deteksi Generator AI
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-red-100 border border-red-200 text-red-800 rounded-full font-montserrat text-[0.65rem] font-bold tracking-wider uppercase">
                <svg className="w-3 h-3 flex-shrink-0" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Tidak untuk Voice-to-Voice (RVC)
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-red-100 border border-red-200 text-red-800 rounded-full font-montserrat text-[0.65rem] font-bold tracking-wider uppercase">
                <svg className="w-3 h-3 flex-shrink-0" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Hindari Noise Berat
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────
      SECTION 6 — FOOTER
      ───────────────────────────────────────── */}
      <footer className="bg-slate-900 text-slate-400 py-16 px-6 lg:px-8 border-t border-slate-800">
        <div ref={footerRef as React.RefObject<HTMLDivElement>} className="max-w-7xl mx-auto">
          <div className={`reveal reveal-fade ${footerVisible ? "reveal-visible" : ""} grid grid-cols-1 md:grid-cols-3 gap-12 mb-12`}>
            <div className="col-span-1 md:col-span-2">
              <div className="font-montserrat text-lg font-black text-white tracking-widest uppercase mb-3">
                VoiceGuard.
              </div>
              <p className="text-sm leading-relaxed max-w-sm">
                Sistem Deteksi Kloning Suara Berbasis Kecerdasan Buatan (Deep Learning) untuk Membedakan Audio Manusia Asli dan Rekaman Sintetik.
              </p>
            </div>
            
            <div>
              <div className="font-montserrat text-[0.65rem] font-bold tracking-[0.2em] uppercase text-slate-500 mb-4">
                Tim Peneliti
              </div>
              <div className="text-sm leading-relaxed text-slate-300">
                <strong>Zakki Farian</strong><br />
                Fakultas Sains & Teknologi<br />
                Universitas Teknologi Yogyakarta<br />
              </div>
            </div>
          </div>
          
          <div className="h-[1px] w-full bg-slate-800 mb-8"></div>
          
          <div className={`reveal reveal-fade ${footerVisible ? "reveal-visible" : ""} reveal-delay-2 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500`}>
            <p>&copy; {new Date().getFullYear()} VoiceGuard. Hak Cipta Dilindungi.</p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">Dokumentasi</a>
              <a href="#" className="hover:text-white transition-colors">Tentang Proyek</a>
              <a href="#" className="hover:text-white transition-colors">GitHub</a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
