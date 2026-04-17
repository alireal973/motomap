"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, MapPin } from "lucide-react";

const navLinks = [
  { label: "Features", href: "#features" },
  { label: "Routes", href: "#routes" },
  { label: "Community", href: "#community" },
  { label: "Pricing", href: "#pricing" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled
            ? "glass-strong py-3"
            : "bg-transparent py-5"
        }`}
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-8">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2.5 group">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-stitch-light to-stitch-mid transition-transform duration-300 group-hover:scale-110">
              <MapPin className="h-5 w-5 text-white" strokeWidth={2.5} />
              <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-br from-stitch-light to-stitch-mid opacity-40 blur-md" />
            </div>
            <span className="text-xl font-bold tracking-tight text-stitch-thread">
              Moto<span className="text-gradient">Map</span>
            </span>
          </a>

          {/* Desktop Nav */}
          <nav className="hidden items-center gap-1 md:flex">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="relative rounded-full px-4 py-2 text-sm font-medium text-stitch-thread/70 transition-colors hover:text-white"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Desktop CTA */}
          <div className="hidden items-center gap-3 md:flex">
            <a
              href="#"
              className="text-sm font-medium text-stitch-thread/70 transition-colors hover:text-white"
            >
              Sign In
            </a>
            <a
              href="#"
              className="relative inline-flex h-10 items-center justify-center gap-2 rounded-full bg-gradient-to-r from-stitch-accent to-[#ff8c5c] px-5 text-sm font-semibold text-white shadow-lg transition-all duration-300 hover:shadow-stitch-accent/30 hover:scale-[1.03] active:scale-[0.98]"
            >
              Get Started
            </a>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="relative z-50 flex h-10 w-10 items-center justify-center rounded-xl glass md:hidden"
            aria-label="Toggle menu"
          >
            {mobileOpen ? (
              <X className="h-5 w-5 text-white" />
            ) : (
              <Menu className="h-5 w-5 text-white" />
            )}
          </button>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="fixed inset-0 z-40 flex flex-col items-center justify-center gap-6 bg-stitch-dark/95 backdrop-blur-xl md:hidden"
          >
            {navLinks.map((link, i) => (
              <motion.a
                key={link.label}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.06 }}
                className="text-2xl font-semibold text-stitch-thread/90 hover:text-white"
              >
                {link.label}
              </motion.a>
            ))}
            <motion.a
              href="#"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-4 inline-flex h-12 items-center justify-center rounded-full bg-gradient-to-r from-stitch-accent to-[#ff8c5c] px-8 text-base font-semibold text-white"
            >
              Get Started
            </motion.a>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
