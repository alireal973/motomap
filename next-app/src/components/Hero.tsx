"use client";

import { motion } from "framer-motion";
import { ArrowRight, Play } from "lucide-react";

const floatingVariants = {
  animate: {
    y: [0, -12, 0],
    transition: { duration: 6, repeat: Infinity, ease: "easeInOut" as const },
  },
};

export default function Hero() {
  return (
    <section className="relative min-h-screen overflow-hidden grain">
      {/* ── Background gradients ── */}
      <div className="pointer-events-none absolute inset-0">
        {/* Primary radial */}
        <div className="absolute left-1/2 top-0 h-[900px] w-[900px] -translate-x-1/2 -translate-y-1/3 rounded-full bg-gradient-to-b from-stitch-mid/25 to-transparent blur-3xl" />
        {/* Accent glow */}
        <div className="absolute right-0 top-1/3 h-[500px] w-[500px] rounded-full bg-stitch-accent/8 blur-[120px]" />
        {/* Grid lines */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
            backgroundSize: "72px 72px",
          }}
        />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-6 pt-24 lg:px-8">
        {/* ── Badge ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-stitch-light/20 bg-stitch-light/5 px-4 py-1.5 text-xs font-medium text-stitch-sky backdrop-blur-sm">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-stitch-accent animate-pulse" />
            Now in Beta — Join 2,400+ riders
          </div>
        </motion.div>

        {/* ── Headline ── */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="max-w-4xl text-center text-5xl font-extrabold leading-[1.08] tracking-tight sm:text-6xl lg:text-7xl"
        >
          <span className="text-stitch-thread">Ride </span>
          <span className="text-gradient">Smarter</span>
          <br />
          <span className="text-stitch-thread/60">Arrive </span>
          <span className="text-gradient-warm">Safer</span>
        </motion.h1>

        {/* ── Subheadline ── */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-6 max-w-2xl text-center text-lg leading-relaxed text-stitch-thread/50 sm:text-xl"
        >
          Traffic density analysis, spatial risk mapping, and lane-filtering optimized routing — 
          up to 13% faster than traditional navigation for motorcycle riders.
        </motion.p>

        {/* ── CTA buttons ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="mt-10 flex flex-col items-center gap-4 sm:flex-row"
        >
          <a
            href="#"
            className="group relative inline-flex h-14 items-center justify-center gap-2.5 rounded-full bg-gradient-to-r from-stitch-accent to-[#ff8c5c] px-8 text-base font-semibold text-white shadow-2xl shadow-stitch-accent/20 transition-all duration-300 hover:shadow-stitch-accent/40 hover:scale-[1.03] active:scale-[0.98]"
          >
            Start Riding Free
            <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-0.5" />
          </a>
          <a
            href="#"
            className="group inline-flex h-14 items-center justify-center gap-2.5 rounded-full border border-white/10 bg-white/[0.03] px-8 text-base font-medium text-stitch-thread/80 backdrop-blur-sm transition-all duration-300 hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
          >
            <Play className="h-4 w-4 text-stitch-light" />
            Watch Demo
          </a>
        </motion.div>

        {/* ── Floating dashboard mockup ── */}
        <motion.div
          variants={floatingVariants}
          animate="animate"
          className="relative mt-20 w-full max-w-5xl"
        >
          <motion.div
            initial={{ opacity: 0, y: 60, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 1.2, delay: 0.9, ease: [0.22, 1, 0.36, 1] }}
            className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.06] to-white/[0.02] p-1 shadow-2xl"
          >
            {/* Inner glow effect */}
            <div className="absolute -top-1/2 left-1/2 h-full w-3/4 -translate-x-1/2 bg-stitch-light/10 blur-[100px]" />

            {/* Dashboard content placeholder */}
            <div className="relative rounded-xl bg-stitch-dark/80 p-6 sm:p-10">
              <div className="grid gap-4 sm:grid-cols-3">
                {/* Stat cards */}
                {[
                  { label: "Avg. Time Saved", value: "13%", color: "from-stitch-light/20 to-stitch-mid/10" },
                  { label: "Risk Zones Mapped", value: "4,800+", color: "from-stitch-accent/20 to-stitch-accent/5" },
                  { label: "Pilot City", value: "İstanbul", color: "from-stitch-gold/20 to-stitch-gold/5" },
                ].map((stat, i) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2 + i * 0.15 }}
                    className={`rounded-xl bg-gradient-to-br ${stat.color} border border-white/5 p-5`}
                  >
                    <p className="text-xs font-medium uppercase tracking-wider text-stitch-thread/40">
                      {stat.label}
                    </p>
                    <p className="mt-2 text-3xl font-bold text-stitch-thread">
                      {stat.value}
                    </p>
                  </motion.div>
                ))}
              </div>

              {/* Map placeholder */}
              <div className="mt-6 h-64 overflow-hidden rounded-xl border border-white/5 bg-gradient-to-br from-stitch-base/20 to-stitch-dark sm:h-80">
                <div className="flex h-full items-center justify-center">
                  <div className="text-center">
                    <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-stitch-light/10">
                      <MapPinIcon />
                    </div>
                    <p className="text-sm text-stitch-thread/30">
                      Interactive route map loads here
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* ── Scroll indicator ── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="mt-12 mb-8"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="flex h-10 w-6 items-start justify-center rounded-full border border-white/20 p-1.5"
          >
            <div className="h-2 w-1 rounded-full bg-stitch-light/60" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

function MapPinIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-stitch-light/50">
      <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}
