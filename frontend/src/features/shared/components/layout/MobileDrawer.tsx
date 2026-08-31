"use client";

import Link from "next/link";
import { X } from "lucide-react";
import { navigation } from "@/features/shared/config/navigation";
import Image from "next/image";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function MobileDrawer({ open, onClose }: Props) {
  return (
    <>
      {open && (
        <div onClick={onClose} className="fixed inset-0 z-40 bg-black/60" />
      )}

      <aside
        className={`
  fixed
  top-0
  left-0
  h-full
  w-70
  z-50
  bg-bg-surface
  border-r
  border-border
  transition-transform
  duration-300
  ${open ? "translate-x-0" : "-translate-x-full"}
`}
      >
        <div
          className="
            flex
            items-center
            justify-between
            h-16
            px-5
            border-b
          "
          style={{
            borderColor: "var(--border)",
          }}
        >
          <Link href="/" className="flex items-center ">
              <Image
                src="/f1lm.png"
                alt="F1 Lightning McQueen"
                width={100}
                height={36}
                priority
                className="h-8 w-auto rounded object-cover"
              />
            </Link>

          <button onClick={onClose}>
            <X className="text-primary" size={18} />
          </button>
        </div>

        <nav className="p-4 flex flex-col gap-1">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className="
                px-3
                py-2
                rounded-md
                text-sm
                text-text-secondary
                hover:text-text-primary
                hover:bg-bg-card
                transition-colors
                "
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
}
