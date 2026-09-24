<?php
/**
 * services/symptom_prediction.php
 * Explainable, deterministic symptom-based disease matching engine for MediSense AI.
 * Evaluates symptom co-occurrence, characteristic vs secondary weighting,
 * and handles overlapping conditions transparently without claiming medical diagnosis.
 */

class SymptomPredictionService {
    private static $diseases = null;
    private static $symptoms = null;

    public static function loadData() {
        if (self::$diseases === null) {
            $path = __DIR__ . '/../data/diseases.json';
            if (file_exists($path)) {
                $raw = file_get_contents($path);
                self::$diseases = json_decode($raw, true) ?: [];
            } else {
                self::$diseases = [];
            }
        }

        if (self::$symptoms === null) {
            $path = __DIR__ . '/../data/symptoms.json';
            if (file_exists($path)) {
                $raw = file_get_contents($path);
                self::$symptoms = json_decode($raw, true) ?: [];
            } else {
                self::$symptoms = [];
            }
        }
    }

    public static function getSymptoms() {
        self::loadData();
        return self::$symptoms;
    }

    public static function getDiseases() {
        self::loadData();
        return self::$diseases;
    }

    /**
     * Normalize natural language user query to standardized symptom key
     */
    public static function normalizeQuery($query) {
        self::loadData();
        $q = strtolower(trim($query));
        if (empty($q)) return null;

        // Exact key match
        foreach (self::$symptoms as $sym) {
            if ($sym['key'] === $q) return $sym['key'];
        }

        // Exact or substring match in name or synonyms
        foreach (self::$symptoms as $sym) {
            if (strtolower($sym['name']) === $q) return $sym['key'];
            foreach ($sym['synonyms'] as $syn) {
                if (strtolower($syn) === $q) return $sym['key'];
            }
        }

        // Partial match
        foreach (self::$symptoms as $sym) {
            if (stripos($sym['name'], $q) !== false) return $sym['key'];
            foreach ($sym['synonyms'] as $syn) {
                if (stripos($syn, $q) !== false) return $sym['key'];
            }
        }

        return null;
    }

    /**
     * Deterministic symptom-matching scoring engine
     */
    public static function matchSymptoms($selectedSymptoms, $context = []) {
        self::loadData();

        if (empty($selectedSymptoms) || count($selectedSymptoms) < 2) {
            return [
                'status' => 'insufficient_information',
                'message' => 'Please select at least 2 symptoms to begin an educational analysis.',
                'conditions' => [],
                'selected_symptoms' => $selectedSymptoms,
                'disclaimer' => self::getDisclaimer()
            ];
        }

        $normalizedList = [];
        foreach ($selectedSymptoms as $sym) {
            $norm = self::normalizeQuery($sym);
            $normalizedList[] = $norm ?: $sym;
        }
        $selectedSet = array_unique(array_filter($normalizedList));
        $results = [];

        foreach (self::$diseases as $d) {
            $common = $d['commonSymptoms'] ?? [];
            $less = $d['lessCommonSymptoms'] ?? [];
            $allSyms = $d['symptoms'] ?? [];

            $matchedCommon = array_values(array_intersect($selectedSet, $common));
            $matchedLess = array_values(array_intersect($selectedSet, $less));
            $allMatched = array_values(array_intersect($selectedSet, $allSyms));

            if (empty($allMatched)) {
                continue;
            }

            // Weights: characteristic symptoms count 3.0, secondary count 1.5
            $wMatched = (count($matchedCommon) * 3.0) + (count($matchedLess) * 1.5);
            $wExpected = (count($common) * 3.0) + (count($less) * 1.5);
            if ($wExpected <= 0) continue;

            $recall = $wMatched / $wExpected;

            // Penalty for selected symptoms that are NOT in the disease profile
            $wSelected = 0.0;
            foreach ($selectedSet as $s) {
                if (in_array($s, $common)) {
                    $wSelected += 3.0;
                } elseif (in_array($s, $less)) {
                    $wSelected += 1.5;
                } else {
                    $wSelected += 2.0; // mismatch penalty
                }
            }

            $precision = $wSelected > 0 ? ($wMatched / $wSelected) : 0;

            // F0.8 balanced score
            $beta = 0.8;
            $betaSq = $beta * $beta;
            if (($betaSq * $precision + $recall) > 0) {
                $fScore = ((1 + $betaSq) * $precision * $recall) / (($betaSq * $precision) + $recall);
            } else {
                $fScore = 0;
            }

            $scoreVal = min(100, max(0, round($fScore * 100)));

            // Filter out low affinity noise
            if ($scoreVal < 20) {
                continue;
            }

            if ($scoreVal >= 70) {
                $matchLevel = 'High';
            } elseif ($scoreVal >= 40) {
                $matchLevel = 'Moderate';
            } else {
                $matchLevel = 'Limited';
            }

            $unmatchedExpected = array_values(array_diff($allSyms, $selectedSet));

            $results[] = [
                'id' => $d['id'],
                'name' => $d['name'],
                'category' => $d['category'],
                'score' => $scoreVal,
                'match_level' => $matchLevel,
                'matched_symptoms' => $allMatched,
                'matched_common' => $matchedCommon,
                'matched_less' => $matchedLess,
                'other_symptoms' => array_slice($unmatchedExpected, 0, 4),
                'description' => $d['description'],
                'causes' => $d['causes'] ?? '',
                'risk_factors' => $d['riskFactors'] ?? [],
                'prevention' => $d['prevention'] ?? [],
                'red_flags' => $d['redFlags'] ?? [],
                'differentiating' => $d['differentiatingFeatures'] ?? '',
                'when_to_seek' => $d['whenToSeekCare'] ?? '',
                'source' => $d['source'] ?? 'CDC Clinical Practice Guidelines / WHO Disease Reference'
            ];
        }

        // Sort descending by score
        usort($results, function($a, $b) {
            return $b['score'] <=> $a['score'];
        });

        // Top 5 conditions
        $topConditions = array_slice($results, 0, 5);

        // Emergency red flags aggregation
        $emergencySigns = [];
        foreach ($topConditions as $tc) {
            foreach ($tc['red_flags'] as $rf) {
                if (!in_array($rf, $emergencySigns)) {
                    $emergencySigns[] = $rf;
                }
            }
        }

        return [
            'status' => 'success',
            'conditions' => $topConditions,
            'selected_symptoms' => $selectedSet,
            'context' => $context,
            'emergency_signs' => array_slice($emergencySigns, 0, 4),
            'disclaimer' => self::getDisclaimer()
        ];
    }

    public static function getDisclaimer() {
        return 'This tool provides educational symptom-based information and is not a medical diagnosis. A qualified healthcare professional should evaluate persistent, severe, or concerning symptoms. If you are experiencing chest pain, difficulty breathing, or severe trauma, call emergency services immediately.';
    }
}
