interface TraitLabel {
  label: string;
  positive: string;
  negative: string;
}

// Directional descriptions for each clustering feature, keyed the same way
// the backend names them. Values are teammate-relative deltas or slopes
// where the sign has a specific real meaning - this maps that sign to
// plain language rather than showing a raw z-score.
const TRAITS: Record<string, TraitLabel> = {
  race_pace_teammate_relative: {
    label: "Race pace vs. teammate",
    negative: "faster than their teammate in the race",
    positive: "slower than their teammate in the race",
  },
  qualifying_pace_teammate_relative: {
    label: "Qualifying pace vs. teammate",
    negative: "faster than their teammate in qualifying",
    positive: "slower than their teammate in qualifying",
  },
  quali_race_delta_teammate_relative: {
    label: "Quali vs. race trend",
    positive: "relatively stronger in the race than in qualifying, vs. their teammate",
    negative: "relatively stronger in qualifying than in the race, vs. their teammate",
  },
  degradation_slope: {
    label: "Tyre degradation",
    negative: "below-average tyre degradation (fuel-corrected)",
    positive: "above-average tyre degradation (fuel-corrected)",
  },
  consistency_cv: {
    label: "Consistency",
    negative: "more consistent lap times than average",
    positive: "less consistent lap times than average",
  },
  start_performance_delta: {
    label: "Start performance",
    positive: "tends to gain positions early in the race",
    negative: "tends to lose positions early in the race",
  },
};

export function describeTraits(centroid: Record<string, number>, count = 2): string[] {
  const entries = Object.entries(centroid)
    .filter(([key]) => key in TRAITS)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, count);

  return entries.map(([key, value]) => {
    const trait = TRAITS[key];
    return value >= 0 ? trait.positive : trait.negative;
  });
}
