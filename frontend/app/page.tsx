import { CompanySearch } from "@/components/search/CompanySearch";

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-950 text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-[-18rem] h-[36rem] w-[36rem] -translate-x-1/2 rounded-full bg-slate-800/20 blur-3xl" />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
        <div className="text-center">
          <div className="inline-flex items-center rounded-full border border-slate-800 bg-slate-900/70 px-3 py-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-[0.25em] text-slate-400">
              FINTENDO
            </span>
          </div>

          <h1 className="mt-7 text-5xl font-semibold tracking-[-0.03em] text-white sm:text-6xl">
            Research, grounded in evidence.
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">
            Fundamental analysis, technical signals, and market intelligence
            synthesized into one research view of any listed Indian company
          </p>
        </div>

        <div className="mx-auto mt-10 w-full max-w-2xl">
          <CompanySearch />
        </div>

        <div className="mx-auto mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-slate-600">
          <span>Fundamental Analysis</span>
          <span>Technical Analysis</span>
          <span>Market Intelligence</span>
          <span>Committee Decision</span>
        </div>
      </div>
    </main>
  );
}