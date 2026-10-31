import { Link } from "react-router-dom";
import { Mic, Brain, TrendingUp } from "lucide-react";

const features = [
  { icon: Mic, title: "Speak, don't memorise", text: "Dictate answers from memory with Wispr Flow." },
  { icon: Brain, title: "AI finds your gaps", text: "Detects missing points and misconceptions, not just right or wrong." },
  { icon: TrendingUp, title: "Adaptive learning", text: "Mastery tracking, smart questions and revision reminders." },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f1b4d] via-[#1e2a78] to-[#5b3fd0] text-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between p-6">
        <span className="text-xl font-bold">🧠 MindMap AI</span>
        <Link to="/teacher" className="text-sm text-slate-200 hover:text-white">For teachers</Link>
      </header>

      <section className="mx-auto max-w-4xl px-6 py-20 text-center">
        <h1 className="text-4xl font-extrabold leading-tight md:text-6xl">
          Don't just learn the answer.<br />Understand what you don't understand.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-200">
          A voice-first AI study tutor that listens to your answers, finds what you missed and
          builds a personal revision plan. Starting with Class 10 Physics: Light.
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Link to="/diagnostic" className="rounded-xl bg-white px-6 py-3 font-semibold text-[#0f1b4d] hover:bg-slate-100">
            Start diagnostic
          </Link>
          <Link to="/dashboard" className="rounded-xl border border-white/40 px-6 py-3 font-semibold hover:bg-white/10">
            View dashboard
          </Link>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-5 px-6 pb-20 md:grid-cols-3">
        {features.map(({ icon: Icon, title, text }) => (
          <div key={title} className="rounded-2xl bg-white/10 p-6 backdrop-blur">
            <Icon className="mb-3" />
            <h3 className="font-semibold">{title}</h3>
            <p className="mt-1 text-sm text-slate-200">{text}</p>
          </div>
        ))}
      </section>
    </div>
  );
}