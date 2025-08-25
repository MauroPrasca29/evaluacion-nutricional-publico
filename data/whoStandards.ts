// Simplified WHO growth standards for boys, 0-24 months
// In a real application, this would be a comprehensive dataset,
// likely fetched from an API or a larger local data file,
// and would differ for boys and girls.

export const whoStandards = {
  weight: Array.from({ length: 25 }, (_, i) => ({
    age: i,
    p3: (2.5 + i * 0.45).toFixed(1),
    p15: (2.9 + i * 0.48).toFixed(1),
    p50: (3.3 + i * 0.5).toFixed(1),
    p85: (3.8 + i * 0.53).toFixed(1),
    p97: (4.2 + i * 0.55).toFixed(1),
  })),
  height: Array.from({ length: 25 }, (_, i) => ({
    age: i,
    p3: (48 + i * 2.0).toFixed(1),
    p15: (49 + i * 2.1).toFixed(1),
    p50: (50 + i * 2.2).toFixed(1),
    p85: (51 + i * 2.3).toFixed(1),
    p97: (52 + i * 2.4).toFixed(1),
  })),
  bmi: Array.from({ length: 25 }, (_, i) => ({
    age: i,
    p3: (11.0 + i * 0.1).toFixed(1),
    p15: (12.0 + i * 0.1).toFixed(1),
    p50: (13.0 + i * 0.05).toFixed(1),
    p85: (14.0 + i * 0.05).toFixed(1),
    p97: (15.0 + i * 0.05).toFixed(1),
  })),
}
