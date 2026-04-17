"use client";

import { useRef } from "react";
import { motion, useInView, useScroll, useTransform } from "framer-motion";
import { Quote } from "lucide-react";

const testimonials = [
  {
    name: "Marco R.",
    role: "Adventure Rider · Italy",
    quote:
      "MotoMap completely changed how I plan my Alpine tours. The curvature data is incredibly accurate.",
    avatar: "MR",
  },
  {
    name: "Sarah K.",
    role: "Weekend Cruiser · Germany",
    quote:
      "I found roads I never knew existed just 30 minutes from home. The community recommendations are golden.",
    avatar: "SK",
  },
  {
    name: "Ryu T.",
    role: "Sport Tourer · Japan",
    quote:
      "The elevation profiling saved me from getting caught in mountain passes during bad weather. Essential tool.",
    avatar: "RT",
  },
];

export default function Testimonials() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  const scrollRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: scrollRef,
    offset: ["start end", "end start"],
  });
  const rotate = useTransform(scrollYProgress, [0, 1], [2, -2]);

  return (
    <section
      id="community"
      ref={scrollRef}
      className="relative py-32 overflow-hidden"
    >
      <div className="pointer-events-none absolute right-1/4 top-0 h-[500px] w-[500px] rounded-full bg-[#a78bfa]/5 blur-[150px]" />

      <div ref={ref} className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-stitch-accent">
            Testimonials
          </p>
          <h2 className="mt-3 text-4xl font-bold tracking-tight text-stitch-thread sm:text-5xl">
            Loved by <span className="text-gradient">Riders</span>
          </h2>
        </motion.div>

        <motion.div style={{ rotateZ: rotate }} className="mt-16 grid gap-6 lg:grid-cols-3">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.15 + i * 0.1 }}
              className="relative rounded-2xl border border-white/[0.06] bg-white/[0.02] p-7"
            >
              <Quote className="mb-4 h-6 w-6 text-stitch-light/20" />
              <p className="text-base leading-relaxed text-stitch-thread/60">
                &ldquo;{t.quote}&rdquo;
              </p>
              <div className="mt-6 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-stitch-light/30 to-stitch-mid/20 text-xs font-bold text-stitch-thread/70">
                  {t.avatar}
                </div>
                <div>
                  <p className="text-sm font-semibold text-stitch-thread/80">
                    {t.name}
                  </p>
                  <p className="text-xs text-stitch-thread/35">{t.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
