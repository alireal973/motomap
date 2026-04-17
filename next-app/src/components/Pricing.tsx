"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Check, X } from "lucide-react";

const plans = [
  {
    name: "Rider",
    price: "Free",
    period: "",
    description: "Essential routing for everyday motorcycle commuters",
    features: [
      { text: "Motorcycle-optimized routing", included: true },
      { text: "Basic traffic density view", included: true },
      { text: "3 saved routes per week", included: true },
      { text: "Risk zone warnings", included: false },
      { text: "Real-time traffic integration", included: false },
      { text: "Route analytics & comparison", included: false },
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Pro Rider",
    price: "$9",
    period: "/mo",
    description: "Up to 13% faster routes with lane filtering advantage",
    features: [
      { text: "Unlimited saved routes", included: true },
      { text: "Lane filtering advantage routing", included: true },
      { text: "Risk zone mapping (KDE analysis)", included: true },
      { text: "Real-time traffic integration", included: true },
      { text: "Elevation & curvature profiles", included: true },
      { text: "Route analytics & comparison", included: true },
    ],
    cta: "Start 14-Day Trial",
    highlighted: true,
  },
  {
    name: "Fleet",
    price: "$29",
    period: "/mo",
    description: "For courier companies and moto-delivery fleets",
    features: [
      { text: "Everything in Pro", included: true },
      { text: "Multi-rider fleet management", included: true },
      { text: "API access & route embedding", included: true },
      { text: "Delivery time optimization", included: true },
      { text: "Fuel cost reduction analytics", included: true },
      { text: "Priority support", included: true },
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

export default function Pricing() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="pricing" className="relative py-32 overflow-hidden">
      <div className="pointer-events-none absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-stitch-mid/6 blur-[150px]" />

      <div ref={ref} className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-sm font-semibold uppercase tracking-widest text-stitch-accent">
            Pricing
          </p>
          <h2 className="mt-3 text-4xl font-bold tracking-tight text-stitch-thread sm:text-5xl">
            Simple, <span className="text-gradient">Transparent</span> Plans
          </h2>
          <p className="mt-5 text-lg text-stitch-thread/45">
            Start free. Upgrade when your adventures demand more.
          </p>
        </motion.div>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.1 + i * 0.1 }}
              className={`relative rounded-2xl border p-8 transition-all duration-500 ${
                plan.highlighted
                  ? "border-stitch-accent/30 bg-gradient-to-b from-stitch-accent/[0.07] to-transparent scale-[1.02] shadow-2xl shadow-stitch-accent/10"
                  : "border-white/[0.06] bg-white/[0.02] hover:border-white/[0.12]"
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-stitch-accent to-[#ff8c5c] px-4 py-1 text-xs font-semibold text-white">
                  Most Popular
                </div>
              )}

              <h3 className="text-lg font-semibold text-stitch-thread">
                {plan.name}
              </h3>
              <p className="mt-1 text-sm text-stitch-thread/40">
                {plan.description}
              </p>

              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-5xl font-bold text-stitch-thread">
                  {plan.price}
                </span>
                {plan.period && (
                  <span className="text-base text-stitch-thread/40">
                    {plan.period}
                  </span>
                )}
              </div>

              <ul className="mt-8 flex flex-col gap-3">
                {plan.features.map((f) => (
                  <li key={f.text} className="flex items-center gap-3">
                    {f.included ? (
                      <Check className="h-4 w-4 shrink-0 text-stitch-light" />
                    ) : (
                      <X className="h-4 w-4 shrink-0 text-stitch-thread/20" />
                    )}
                    <span
                      className={`text-sm ${
                        f.included
                          ? "text-stitch-thread/70"
                          : "text-stitch-thread/25"
                      }`}
                    >
                      {f.text}
                    </span>
                  </li>
                ))}
              </ul>

              <a
                href="#"
                className={`mt-8 flex h-12 w-full items-center justify-center rounded-xl text-sm font-semibold transition-all duration-300 ${
                  plan.highlighted
                    ? "bg-gradient-to-r from-stitch-accent to-[#ff8c5c] text-white shadow-lg shadow-stitch-accent/20 hover:shadow-stitch-accent/40 hover:scale-[1.02] active:scale-[0.98]"
                    : "border border-white/10 bg-white/[0.03] text-stitch-thread/70 hover:bg-white/[0.06] hover:text-white"
                }`}
              >
                {plan.cta}
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
