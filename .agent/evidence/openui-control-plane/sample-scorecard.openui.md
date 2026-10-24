```openui-lang
score = HermeticScorecard("compare", "defer", "Held-out stub_student_rate=1.000 vs retrieval=1.000 (delta=0.000) does not justify large-GPU expansion. Keep specialized-model-level-3 DEFERRED; continue N3 evidence accumulation.", "context_efficiency, difficulty_calibration, project_state_accuracy, review_precision, routing_effectiveness, skill_reuse, training_effectiveness", "context_efficiency:0.0, difficulty_calibration:0.0, project_state_accuracy:0.0, review_precision:0.0, routing_effectiveness:0.0, skill_reuse:0.0")
rec = RecommendationCard("Level 3", "defer", "Held-out stub_student_rate=1.000 vs retrieval=1.000 (delta=0.000) does not justify large-GPU expansion. Keep specialized-model-level-3 DEFERRED; continue N3 evidence accumulation.")
badge = CompassStatusBadge("Adaptive", "1.74.0", "defer")
root = NorthStarStack([badge, score, rec])
```
