# Assessment guide and primary sources

Research checked 2026-10-10. These are decision aids, not findings about a particular repository. Follow relevant links
and verify versions, device capabilities, and host-process compatibility.

## Rendering and backend decisions

Build a target capability matrix: implemented backend, supported OS/GPU/API level, shader toolchain, required features,
fallback, packaging, and tests. Keep rasterization, compute, ray tracing, and presentation distinct; a partial compute
backend does not establish a full renderer. Compare maintaining the existing backend, a narrow optional backend, and
full migration against product needs and team capacity.

Trace creation, use, synchronization, and destruction across CPU threads, frames in flight, windows, and native
processes. Inspect descriptors/bindings, buffers/textures, render-target lifetime, transient memory, pass
inputs/outputs, layout transitions, and state leakage. Consider explicit pass declarations or a render graph when
observed dependency/lifetime complexity justifies them.

Vulkan validation detects invalid API usage and belongs in development checks; its overhead changes performance, so
separate validation from release benchmarks. Check synchronization against concrete producers and
consumers. [Khronos validation overview](https://docs.vulkan.org/guide/latest/validation_overview.html), [Khronos synchronization examples](https://docs.vulkan.org/guide/latest/synchronization_examples.html).

OpenGL debug callbacks supply diagnostics; timer queries support GPU timestamps. Check API/extension support and
retrieve results asynchronously to avoid profiling-induced
stalls. [Khronos debug callback reference](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDebugMessageCallback.xhtml), [Khronos timestamp query reference](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glQueryCounter.xhtml).

Xcode's Metal performance tools offer GPU timeline and shader profiling evidence. Select capture workflows supported by
the actual backend and
host. [Apple GPU performance guide](https://developer.apple.com/documentation/xcode/optimizing-gpu-performance).

## Shaders, assets, and tooling

Trace shader sources/artifacts through includes/defines, compilation, caching, version targets, packaging, load
failures, and material binding. Inspect representative variants rather than assuming variant count is a problem. Check
pass ordering, shadows, transparency/overdraw, texture formats, mipmaps, color-space conversions, and CPU/GPU layout
agreement. Separate correctness findings from unmeasured optimization hypotheses.

Trace asset identity, import settings, dependencies, cache invalidation, upload budgets, ownership, and disposal.
Separate background CPU preparation from GPU uploads. For editors inspect undo/redo, incremental updates, serialization
fidelity, diagnostics, reimport, and runtime parity. Preserve documented format, threading, and native isolation rules.

## Profiling strategy

Use representative scenarios: cold project load, first shader use, steady rendering, large asset import,
selection/editing, and simulation. Record revision, build mode, OS, JDK, GPU/driver, scene, resolution, quality, warmup,
duration, repetitions, and profiler overhead. Distinguish vsync/caps from bottlenecks and steady work from
compilation/loading spikes.

Separate CPU frame/submission time from GPU execution. Select relevant metrics: p50/p95/p99 frame time, pass timings,
draw/state changes, uploads/readbacks, peak JVM/native/GPU memory, allocations, GC pauses, and editor input latency. CPU
timings around asynchronous graphics calls do not measure GPU execution.

JDK Flight Recorder can investigate CPU, allocation, GC, locking, and I/O; it does not replace GPU
profiling. [Oracle JFR troubleshooting guide](https://docs.oracle.com/en/java/javase/13/troubleshoot/troubleshoot-performance-issues-using-jfr.html)
is version-specific; confirm runtime compatibility.

Without measurements, propose a bounded experiment to distinguish CPU, GPU, synchronization, and loading bottlenecks.
Label target budgets as proposed acceptance criteria. Check that optimizations preserve correctness and do not merely
shift costs to another phase.

## Build, tests, and delivery

Inspect task inputs/outputs, native/shader dependencies, classifiers/ABIs, runtime classpaths, CI runners, distribution
contents, and startup smoke tests. Measure clean, incremental, no-change, and CI builds separately. Build cache and
configuration cache address different work; check compatibility and reproducibility before recommending
either. [Gradle performance guide](https://docs.gradle.org/current/userguide/performance.html).

Match validation to risk: deterministic math/serialization tests, resource/asset integration tests, backend
smoke/conformance checks, image comparisons with justified tolerances, and artifact checks for shaders/natives. Record
hardware exclusions and tests not run. Compare onboarding and architecture documentation with current code.

## Recommendation example

Hypothetical observation: a traced import path uploads textures on the UI thread, but timing data is unavailable.
Recommend measuring UI-block duration during a fixed large import before redesigning scheduling. Rationale: distinguish
preparation from upload stalls. Expected impact: attributable baseline and justified scheduling decision. Effort: 1–2
person-days assuming a profiling hook. Implementation risk: low for instrumentation; leaving the issue unresolved risks
import-time freezes. Dependencies: disposable assets and representative hardware. Success: repeatable CPU/GPU traces and
p95 interaction delay, followed by an accept/fix decision against an agreed latency budget. This supplies no evidence
about the user's code.
