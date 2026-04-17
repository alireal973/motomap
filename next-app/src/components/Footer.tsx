"use client";

import { MapPin } from "lucide-react";

const footerLinks = {
  Product: ["Features", "Routes", "Pricing", "Changelog"],
  Community: ["Discord", "Forums", "Events", "Ambassadors"],
  Company: ["About", "Blog", "Careers", "Contact"],
  Legal: ["Privacy", "Terms", "Security", "Cookies"],
};

export default function Footer() {
  return (
    <footer className="relative border-t border-white/[0.06] bg-stitch-dark">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[1.5fr_1fr_1fr_1fr_1fr]">
          {/* Brand column */}
          <div>
            <a href="#" className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-stitch-light to-stitch-mid">
                <MapPin className="h-4 w-4 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-lg font-bold text-stitch-thread">
                Moto<span className="text-gradient">Map</span>
              </span>
            </a>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-stitch-thread/35">
              The motorcycle route platform built by riders, for riders.
              Navigate every curve with confidence.
            </p>
            <div className="mt-6 flex gap-3">
              {["GH", "X"].map((label, i) => (
                <a
                  key={i}
                  href="#"
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.06] bg-white/[0.02] text-xs font-bold text-stitch-thread/40 transition-all hover:border-white/[0.12] hover:text-white"
                >
                  {label}
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-xs font-semibold uppercase tracking-widest text-stitch-thread/50">
                {category}
              </h4>
              <ul className="mt-4 flex flex-col gap-3">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-stitch-thread/35 transition-colors hover:text-stitch-thread/80"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-16 flex flex-col items-center justify-between gap-4 border-t border-white/[0.04] pt-8 sm:flex-row">
          <p className="text-xs text-stitch-thread/25">
            © {new Date().getFullYear()} MotoMap. All rights reserved.
          </p>
          <div className="flex items-center gap-1 text-xs text-stitch-thread/25">
            <span>Built with</span>
            <span className="text-stitch-accent">♥</span>
            <span>for the riding community</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
