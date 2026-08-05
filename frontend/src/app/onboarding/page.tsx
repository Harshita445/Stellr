"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Check, ArrowRight, X, Star, Users, ChevronDown } from "lucide-react";
import { SectionCombobox } from "@/components/onboarding/section-combobox";
import { FriendPicker } from "@/components/onboarding/friend-picker";
import { api, FriendSearchResult } from "@/lib/api-client";
import { Button } from "@/components/ui/button";

const stagger = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

type Step = "register" | "confirm" | "people" | "done";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("register");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [rollNumber, setRollNumber] = useState("");
  const [sectionCode, setSectionCode] = useState<string | null>(null);
  const [claimedUserId, setClaimedUserId] = useState<string | null>(null);
  const [addedPeople, setAddedPeople] = useState<FriendSearchResult[]>([]);

  const handleRegister = useCallback(async () => {
    if (!name.trim() || !rollNumber.trim() || !sectionCode) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.auth.register(rollNumber, name, sectionCode);
      if (!data.is_new_account) {
        setStep("confirm");
        return;
      }
      localStorage.setItem("access_token", data.tokens!.access_token);
      localStorage.setItem("refresh_token", data.tokens!.refresh_token);
      localStorage.setItem("device_id", data.tokens!.device_id);
      setClaimedUserId(data.user.id);
      setStep("people");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [name, rollNumber, sectionCode]);

  const handleClaim = useCallback(async () => {
    if (!rollNumber.trim() || !sectionCode) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.auth.claim(rollNumber, name, sectionCode);
      localStorage.setItem("access_token", data.tokens.access_token);
      localStorage.setItem("refresh_token", data.tokens.refresh_token);
      localStorage.setItem("device_id", data.tokens.device_id);
      setClaimedUserId(data.user.id);
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign-in failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [rollNumber, name, sectionCode, router]);

  const handleSkip = useCallback(() => {
    router.push("/dashboard");
  }, [router]);

  const handleContinueWithPeople = useCallback(() => {
    router.push("/dashboard");
  }, [router]);

  const slideVariants = {
    enter: { opacity: 0, x: 20 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-[420px] sm:max-w-[460px]">
        <AnimatePresence mode="wait">
          {step === "register" && (
            <motion.div
              key="register"
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="space-y-6"
            >
              <div className="text-center space-y-2">
                <div className="flex items-center justify-center gap-2.5 mb-1">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center shrink-0">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-xl font-bold text-text-primary tracking-tight">
                    Stellr
                  </span>
                </div>
                <p className="text-sm text-text-muted">
                  Your people. Your time. Aligned.
                </p>
              </div>

              <div className="relative overflow-hidden glass rounded-2xl p-5 border border-white/[0.08]">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(139,92,246,0.08)_0%,transparent_70%)] pointer-events-none" />
                <div className="relative z-10 space-y-4">
                  <div>
                    <label className="text-xs text-text-muted block mb-1.5">Name</label>
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Jane Doe"
                      required
                      className="w-full bg-space-700/50 border border-space-400/30 rounded-lg px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted/50 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/50 transition-all duration-200"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-text-muted block mb-1.5">Roll Number</label>
                    <input
                      value={rollNumber}
                      onChange={(e) => setRollNumber(e.target.value)}
                      placeholder="e.g. 22CS001"
                      required
                      className="w-full bg-space-700/50 border border-space-400/30 rounded-lg px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted/50 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/50 transition-all duration-200"
                    />
                  </div>
                  <SectionCombobox value={sectionCode} onChange={setSectionCode} />

                  {error && (
                    <p className="text-sm text-status-busy">{error}</p>
                  )}

                  <Button
                    variant="primary"
                    size="md"
                    className="w-full"
                    disabled={loading || !name.trim() || !rollNumber.trim() || !sectionCode}
                    onClick={handleRegister}
                  >
                    {loading ? "Creating account..." : "Get started"}
                  </Button>
                </div>
              </div>
            </motion.div>
          )}

          {step === "confirm" && (
            <motion.div
              key="confirm"
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="space-y-6"
            >
              <div className="text-center space-y-2">
                <div className="flex items-center justify-center gap-2.5 mb-1">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center shrink-0">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-xl font-bold text-text-primary tracking-tight">
                    Stellr
                  </span>
                </div>
              </div>

              <div className="relative overflow-hidden glass rounded-2xl p-5 border border-white/[0.08]">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(139,92,246,0.08)_0%,transparent_70%)] pointer-events-none" />
                <div className="relative z-10 space-y-4">
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 rounded-full bg-primary-500/15 flex items-center justify-center mx-auto">
                      <Users className="w-6 h-6 text-primary-400" />
                    </div>
                    <p className="text-sm text-text-primary font-medium">
                      Account already exists
                    </p>
                    <p className="text-xs text-text-muted leading-relaxed">
                      An account with this roll number already exists. If this
                      is your account and you&apos;re signing in on a new
                      device, continue below. If this isn&apos;t you, stop
                      here.
                    </p>
                  </div>

                  {error && (
                    <p className="text-sm text-status-busy">{error}</p>
                  )}

                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      size="md"
                      className="flex-1"
                      onClick={() => { setStep("register"); setError(null); }}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      size="md"
                      className="flex-1"
                      disabled={loading}
                      onClick={handleClaim}
                    >
                      {loading ? "Signing in..." : "Continue"}
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {step === "people" && (
            <motion.div
              key="people"
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="space-y-6"
            >
              <div className="text-center space-y-2">
                <div className="flex items-center justify-center gap-2.5 mb-1">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center shrink-0">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-xl font-bold text-text-primary tracking-tight">
                    Stellr
                  </span>
                </div>
              </div>

              <div className="relative overflow-hidden glass rounded-2xl p-5 border border-white/[0.08]">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(139,92,246,0.08)_0%,transparent_70%)] pointer-events-none" />
                <div className="relative z-10 space-y-4">
                  <div className="text-center">
                    <p className="text-sm text-text-primary font-medium">
                      Add a few people
                    </p>
                    <p className="text-xs text-text-muted mt-1">
                      You&apos;ll want to plan around — you can always do
                      this later
                    </p>
                  </div>

                  <FriendPicker
                    currentUserId={claimedUserId || ""}
                    onPeopleChange={setAddedPeople}
                  />

                  <div className="flex gap-2 pt-1">
                    <Button
                      variant="ghost"
                      size="md"
                      className="flex-1"
                      onClick={handleSkip}
                    >
                      Skip for now
                    </Button>
                    <Button
                      variant="primary"
                      size="md"
                      className="flex-1"
                      onClick={handleContinueWithPeople}
                    >
                      {addedPeople.length > 0
                        ? `Continue (${addedPeople.length})`
                        : "Continue"}
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
