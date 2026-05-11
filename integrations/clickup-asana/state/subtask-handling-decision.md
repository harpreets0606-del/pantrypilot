# Subtask Handling Decision (gap #5)

**Recommendation: Flatten subtasks into their own Asana sections based on their own status.**

Reasoning: Across the four parent tasks inspected (ZBR-2801, ZBR-2796, ZBR-2812, ZBR-2846, ZBR-2800, ZBR-2925), subtasks frequently diverge from their parent's status. Concrete evidence:

- **ZBR-2801 (Campaign Strategy, "client review")** has 5 subtasks split across 3 distinct statuses: 3 in "client review" (ZBR-2802, ZBR-2805, ZBR-2806), 2 in "not started" (ZBR-2803, ZBR-2804).
- **ZBR-2812 (Flow expansion, "working on it")** has 2 subtasks neither sharing the parent state: ZBR-2813 "not started", ZBR-2814 "client review".
- **ZBR-2846 (Toniq Stock Sync, "with external")** has 4 subtasks across 3 statuses: ZBR-1501 "not started", ZBR-2792 "on hold", ZBR-2845 "done", ZBR-2849 "done".
- **ZBR-2800 (Database Growth Strategy, "done")** has subtasks in 3 different statuses including 1 "client review" (ZBR-2887) and 1 "not started" (ZBR-2889) — i.e., the parent is closed but subtasks are still open.
- Only ZBR-2796 (Account Setup Review) had subtasks all matching parent ("done").

Because Asana subtasks inherit visibility from the parent's section and cannot themselves live in a different section, treating these as Asana-native subtasks would hide active work under closed parents (e.g., ZBR-2887 buried under a Done ZBR-2800) and would prevent assignees from seeing their own work in the section that matches its real state. Flattening ensures every CU task surfaces in the Asana section that matches its current status, preserves the parent linkage as a description-prefix or tag (e.g., "Parent: ZBR-2801"), and avoids the "subtask zombie" problem in 4 of 5 inspected parents.
