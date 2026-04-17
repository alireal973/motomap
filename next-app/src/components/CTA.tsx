"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { ArrowRight, ChevronRight } from "lucide-react";

export default function CTA() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section className="relative py-32 overflow-hidden">
      {/* Centered glow */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-stitch-accent/10 blur-[150px]" />

      <div ref={ref} className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.97 }}
          animate={isInView ? { opacity: 1, y: 0, scale: 1 } : {}}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
          className="relative overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-br from-stitch-base/30 via-stitch-dark to-stitch-dark p-12 sm:p-16 lg:p-20"
        >
          {/* Decorative grid */}
          <div
            className="pointer-events-none absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage:
                "radial-gradient(rgba(255,255,255,0.3) 1px, transparent 1px)",
              backgroundSize: "24px 24px",
            }}
          />

          {/* Floating orbs */}
          <div className="pointer-events-none absolute -right-20 -top-20 h-60 w-60 rounded-full bg-stitch-accent/15 blur-[80px]" />
          <div className="pointer-events-none absolute -bottom-20 -left-20 h-60 w-60 rounded-full bg-stitch-light/10 blur-[80px]" />

          <div className="relative mx-auto max-w-3xl text-center">
            <motion.p
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ delay: 0.2 }}
              className="text-sm font-semibold uppercase tracking-widest text-stitch-accent"
            >
              Ready to Ride?
            </motion.p>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="mt-4 text-4xl font-bold tracking-tight text-stitch-thread sm:text-5xl lg:text-6xl"
            >
              Your Next Adventure{" "}
              <span className="text-gradient-warm">Starts Here</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 15 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.45 }}
              className="mt-6 text-lg text-stitch-thread/45"
            >
              Join thousands of riders already mapping their dream routes.
              Free forever for basic riders — upgrade when you&apos;re ready.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.6 }}
              className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center"
            >
              <a
                href="#"
                className="group relative inline-flex h-14 items-center gap-2.5 rounded-full bg-gradient-to-r from-stitch-accent to-[#ff8c5c] px-8 text-base font-semibold text-white shadow-2xl shadow-stitch-accent/25 transition-all duration-300 hover:shadow-stitch-accent/40 hover:scale-[1.03] active:scale-[0.98]"
              >
                Create Free Account
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </a>
              <a
                href="#"
                className="inline-flex items-center gap-1.5 text-sm font-medium text-stitch-thread/60 transition-colors hover:text-white"
              >
                View Pricing
                <ChevronRight className="h-3.5 w-3.5" />
              </a>
            </motion.div>

            {/* Trust badges */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ delay: 0.8 }}
              className="mt-12 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs text-stitch-thread/30"
            >
              <span>✓ No credit card required</span>
              <span>✓ 14-day Pro trial</span>
              <span>✓ Cancel anytime</span>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
