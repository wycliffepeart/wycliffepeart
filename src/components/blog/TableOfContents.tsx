"use client";

import { useEffect, useRef, useState } from "react";
import type { TocItem } from "@/lib/toc";

export default function TableOfContents({ items }: { items: TocItem[] }) {
  const [activeId, setActiveId] = useState<string>(items[0]?.id ?? "");
  const [atBottom, setAtBottom] = useState(false);
  const visibleIds = useRef<Set<string>>(new Set());

  useEffect(() => {
    const headingElements = items
      .map((item) => document.getElementById(item.id))
      .filter((el): el is HTMLElement => el !== null);

    if (headingElements.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            visibleIds.current.add(entry.target.id);
          } else {
            visibleIds.current.delete(entry.target.id);
          }
        }

        const firstVisible = items.find((item) => visibleIds.current.has(item.id));
        if (firstVisible) {
          setActiveId(firstVisible.id);
        }
      },
      { rootMargin: "-80px 0px -70% 0px", threshold: 0 },
    );

    headingElements.forEach((el) => observer.observe(el));

    const handleScroll = () => {
      const scrolledToBottom =
        window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;
      setAtBottom(scrolledToBottom);
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", handleScroll);
    };
  }, [items]);

  if (items.length === 0) return null;

  const displayActiveId = atBottom ? items[items.length - 1].id : activeId;

  return (
    <nav className="toc" aria-label="Table of contents">
      <p className="toc-title">On this page</p>
      <ul className="toc-list">
        {items.map((item) => (
          <li
            key={item.id}
            className={`toc-item toc-depth-${item.depth}${item.id === displayActiveId ? " active" : ""}`}
          >
            <a href={`#${item.id}`}>{item.text}</a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
