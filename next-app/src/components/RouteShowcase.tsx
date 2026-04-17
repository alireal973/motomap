"use client";

import { useRef } from "react";
import { motion, useInView, useScroll, useTransform } from "framer-motion";
import { Star, Clock, Mountain, ArrowUpRight } from "lucide-react";

const routes = [
  {
    name: "Transfăgărășan Pass",
    location: "Romania",
    rating: 4.9,
    distance: "151 km",
    elevation: "2,042 m",
    curvature: "Extreme",
    gradient: "from-stitch-accent/30 to-stitch-accent/5",
    border: "border-stitch-accent/20",
  },
  {
    name: "Stelvio Pass",
    location: "Italy",
    rating: 4.8,
    distance: "24.3 km",
    elevation: "2,757 m",
    curvature: "Legendary",
    gradient: "from-stitch-light/30 to-stitch-light/5",
    border: "border-stitch-light/20",
  },
  {
    name: "Tail of the Dragon",
    location: "Tennessee, USA",
    rating: 4.7,
    distance: "17.7 km",
    elevation: "597 m",
    curvature: "318 Curves",
    gradient: "from-stitch-gold/30 to-stitch-gold/5",
    border: "border-stitch-gold/20",
  },
];

export default function RouteShowcase() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  const scrollRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: scrollRef,
    offset: ["start end", "end start"],
  });
  const xShift = useTransform(scrollYProgress, [0, 1], [0, -40]);

  return (
    <section
      id="routes"
      ref={scrollRef}
      className="relative py-32 overflow-hidden"
    >
      {/* Background */}
      <div className="pointer-events-none absolute right-0 top-0 h-[700px] w-[700px] translate-x-1/3 rounded-full bg-stitch-light/5 blur-[180px]" />

      <div ref={ref} className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end"
        >
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-stitch-accent">
              Popular Routes
            </p>
            <h2 className="mt-3 text-4xl font-bold tracking-tight text-stitch-thread sm:text-5xl">
              Legendary <span className="text-gradient">Roads</span>
            </h2>
            <p className="mt-4 max-w-lg text-lg text-stitch-thread/45">
              Handpicked by the community. Rated by thousands of riders worldwide.
            </p>
          </div>
          <a
            href="#"
            className="group inline-flex items-center gap-2 text-sm font-semibold text-stitch-light transition-colors hover:text-white"
          >
            View All Routes
            <ArrowUpRight className="h-4 w-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </a>
        </motion.div>

        {/* Route cards */}
        <motion.div style={{ x: xShift }} className="mt-14 grid gap-6 lg:grid-cols-3">
          {routes.map((route, i) => (
            <motion.div
              key={route.name}
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.15 + i * 0.12 }}
              className={`group relative overflow-hidden rounded-2xl border ${route.border} bg-gradient-to-br ${route.gradient} p-6 transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl`}
            >
              {/* Top row */}
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-stitch-thread">
                    {route.name}
                  </h3>
                  <p className="mt-1 text-sm text-stitch-thread/50">
                    {route.location}
                  </p>
                </div>
                <div className="flex items-center gap-1 rounded-full bg-white/10 px-2.5 py-1">
                  <Star className="h-3.5 w-3.5 fill-stitch-gold text-stitch-gold" />
                  <span className="text-xs font-semibold text-stitch-thread">
                    {route.rating}
                  </span>
                </div>
              </div>

              {/* Stats */}
              <div className="mt-6 grid grid-cols-3 gap-4">
                {[
                  { icon: Clock, label: "Distance", value: route.distance },
                  { icon: Mountain, label: "Elevation", value: route.elevation },
                  {
                    icon: () => (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 12c-2 0-3-1-3-3s1-3 3-3" />
                        <path d="M3 12c2 0 3 1 3 3s-1 3-3 3" />
                        <path d="M21 12H3" />
                      </svg>
                    ),
                    label: "Curvature",
                    value: route.curvature,
                  },
                ].map((stat) => (
                  <div key={stat.label}>
                    <div className="flex items-center gap-1.5 text-stitch-thread/35">
                      <stat.icon className="h-3.5 w-3.5" />
                      <span className="text-[10px] font-medium uppercase tracking-wider">
                        {stat.label}
                      </span>
                    </div>
                    <p className="mt-1 text-sm font-semibold text-stitch-thread/80">
                      {stat.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* Fake elevation chart */}
              <div className="mt-6 h-20 w-full overflow-hidden rounded-lg border border-white/5 bg-white/[0.03]">
                <svg
                  viewBox="0 0 400 80"
                  fill="none"
                  className="h-full w-full"
                  preserveAspectRatio="none"
                >
                  <defs>
                    <linearGradient id={`grad-${i}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="rgba(109,180,216,0.3)" />
                      <stop offset="100%" stopColor="rgba(109,180,216,0)" />
                    </linearGradient>
                  </defs>
                  <path
                    d={`M0,60 Q50,${50 - i * 10} 100,${40 - i * 5} T200,${30 + i * 5} T300,${20 + i * 8} T400,${45 - i * 3}`}
                    stroke="rgba(109,180,216,0.5)"
                    strokeWidth="2"
                    fill="none"
                  />
                  <path
                    d={`M0,60 Q50,${50 - i * 10} 100,${40 - i * 5} T200,${30 + i * 5} T300,${20 + i * 8} T400,${45 - i * 3} V80 H0 Z`}
                    fill={`url(#grad-${i})`}
                  />
                </svg>
              </div>

              {/* CTA */}
              <a
                href="#"
                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] py-3 text-sm font-medium text-stitch-thread/70 transition-all duration-300 hover:bg-white/[0.08] hover:text-white"
              >
                Explore Route
                <ArrowUpRight className="h-3.5 w-3.5" />
              </a>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
