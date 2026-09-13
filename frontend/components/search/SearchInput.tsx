"use client";

import { Search } from "lucide-react";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search company or ticker...",
}: SearchInputProps) {
  return (
    <div className="relative">
      <Search
        size={20}
        className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
      />

      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="h-14 w-full rounded-xl border border-slate-800 bg-slate-900/80 pl-12 pr-4 text-base text-slate-100 outline-none placeholder:text-slate-500 transition focus:border-slate-600 focus:ring-1 focus:ring-slate-600"
        autoComplete="off"
      />
    </div>
  );
}