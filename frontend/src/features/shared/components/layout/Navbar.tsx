"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import SearchBar from "./SearchBar";
import SearchModal from "./SearchModal";
import MobileDrawer from "./MobileDrawer";
import { navigation } from "@/features/shared/config/navigation";
import Image from "next/image";

export default function Navbar() {
  const pathname = usePathname();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <>
      <header
        className="
        sticky
        top-0
        z-30
        lg:h-16
        bg-bg-surface/90
        backdrop-blur-md
        border-b
        border-border
        "
      >
        <div
          className="
            mx-auto
            max-w-[1600px]
            h-full
            px-6
            flex
            items-center
            justify-between
          "
        >
          {/* LEFT */}
          <div
            className="
              flex
              items-center
              gap-8
            "
          >
            <Link href="/" className="flex items-center ">
              <Image
                src="/f1lm.png"
                alt="F1 Lightning McQueen"
                width={160}
                height={50}
                priority
                className="bg-slate-200 rounded max-lg:hidden"
              />
            </Link>

            <nav
              className="
                 hidden
                lg:flex
                items-center
                gap-1
              "
            >
              {navigation.map((item) => {
                const active = pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`
                        px-3
                        py-2
                        rounded-md
                        text-sm
                        transition-colors
                        border
                        ${
                          active
                            ? "bg-primary/10 border-primary/20 text-text-primary"
                            : "border-transparent text-text-secondary hover:text-text-primary hover:bg-bg-card"
                        }
                        `}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* RIGHT */}
          <div
            className="
              hidden
              lg:flex
              items-center
              gap-3
            "
          >
            <SearchBar onOpen={() => setSearchOpen(true)} />
          </div>

          {/* MOBILE */}
          <div
            className="
                flex
                lg:hidden
                flex-col
                gap-3
                w-full
                py-4
            "
          >
            <Link href="/" className="flex justify-center">
              <Image
                src="/f1lm.png"
                alt="F1 Lightning McQueen"
                width={140}
                height={44}
                priority
              />
            </Link>

            <div className="flex items-center gap-2">
              <div className="flex-1">
                <SearchBar onOpen={() => setSearchOpen(true)} />
              </div>

              <button
                onClick={() => setDrawerOpen(true)}
                className="
                    h-10
                    w-10

                    flex
                    items-center
                    justify-center

                    rounded-lg

                    bg-bg-card
                    border
                    border-border

                    text-text-secondary
                    hover:text-text-primary
                    hover:bg-bg-hover

                    transition-colors
                "
              >
                <Menu size={18} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
      {searchOpen && <SearchModal onClose={() => setSearchOpen(false)} />}
    </>
  );
}
