"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import {
  Map,
  BarChart3,
  Users,
  Shield,
  Navigation,
  Zap,
} from "lucide-react";

const features = [
  {
    icon: Map,
    title: "Traffic Density Analysis",
    description:
      "Real-time and simulated traffic density data integrated with Istanbul's road network via OSMnx and GeoPandas.",
    gradient: "from-stitch-light to-stitch-mid",
    glow: "bg-stitch-light/15",
  },
  {
    icon: Shield,
    title: "Risk Zone Mapping",
    description:
      "Kernel Density Estimation (KDE) based crash hotspot analysis — visualize danger zones before you ride.",
    gradient: "from-stitch-accent to-[#ff8c5c]",
    glow: "bg-stitch-accent/15",
  },
  {
    icon: Navigation,
    title: "Optimized Motorcycle Routing",
    description:
      "Dijkstra & A* algorithms with motorcycle-specific cost functions — lane filtering advantage built in.",
    gradient: "from-stitch-gold to-[#f6a549]",
    glow: "bg-stitch-gold/15",
  },
  {
    icon: BarChart3,
    title: "Elevation & Curvature Profiles",
    description:
      "Detailed elevation and road geometry data for every route segment, anticipating climbs and turns.",
    gradient: "from-[#a78bfa] to-[#7c3aed]",
    glow: "bg-[#a78bfa]/15",
  },
  {
    icon: Zap,
    title: "Lane Filtering Advantage",
    description:
      "Unique model based on academic research — motorcycles gain speed in congested multi-lane roads.",
    gradient: "from-emerald-400 to-emerald-600",
    glow: "bg-emerald-400/15",
  },
  {
    icon: Users,
    title: "Fleet & Delivery Optimization",
    description:
      "Reduce delivery times and fuel costs for courier companies with motorcycle-optimized fleet routing.",
    gradient: "from-stitch-sky to-stitch-light",
    glow: "bg-stitch-sky/15",
  },
];

export default function Features() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" className="relative py-32 overflow-hidden">
      {/* Background glow */}
      <div className="pointer-events-none absolute left-0 top-1/4 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-stitch-mid/8 blur-[150px]" />

      <div ref={ref} className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-stitch-accent">
            Features
          </p>
          <h2 className="mt-3 text-4xl font-bold tracking-tight text-stitch-thread sm:text-5xl">
            Built for{" "}
            <span className="text-gradient">Serious Riders</span>
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-stitch-thread/45">
            Everything you need to plan, ride, and relive the perfect motorcycle adventure — all in one platform.
          </p>
        </motion.div>

        {/* Feature grid */}
        <div className="mt-20 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{
                duration: 0.6,
                delay: 0.1 + i * 0.08,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="group relative rounded-2xl border border-white/[0.06] bg-white/[0.02] p-7 transition-all duration-500 hover:border-white/[0.12] hover:bg-white/[0.04]"
            >
              {/* Icon */}
              <div className="relative mb-5 inline-flex">
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${feature.gradient} shadow-lg`}
                >
                  <feature.icon className="h-5 w-5 text-white" strokeWidth={2} />
                </div>
                <div
                  className={`absolute -inset-2 -z-10 rounded-2xl ${feature.glow} blur-xl opacity-0 transition-opacity duration-500 group-hover:opacity-100`}
                />
              </div>

              {/* Text */}
              <h3 className="text-lg font-semibold text-stitch-thread">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-stitch-thread/40">
                {feature.description}
              </p>

              {/* Hover corner accent */}
              <div className="absolute right-4 top-4 h-8 w-8 rounded-full bg-gradient-to-br from-white/[0.03] to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
