# Desperta

**An iOS alarm that only stops once you actually get up**
**Stack** Swift · iOS 26 · AlarmKit · Vision · XcodeGen
**Repository** [limamarcelinog/early](https://github.com/limamarcelinog/early) *(private — available on request)*

---

## The idea

Every "smart alarm" has the same flaw: the thing that dismisses it is reachable from the bed. Shake it, solve a maths problem, scan a QR code — all doable half-asleep, and all defeated by the fact that you never left the mattress.

Desperta rings with the authority of the native Clock app, using **AlarmKit**, so it cuts through silent mode and focus modes the way a third-party alarm normally cannot. It stops only after a **physical mission verified by the camera** — you have to be somewhere else, doing something, and the Vision framework confirms it.

## Engineering notes

**The domain is a separate Swift package, tested without a device.** The alarm's rules — scheduling, mission state, what counts as completion — live in a `Domain` package with its own test suite that runs on the command line. `make test` needs no iPhone and no simulator, which means the logic can be developed and verified in a tight loop instead of through a multi-minute build-and-deploy cycle.

**A type-check target that does not require the full toolchain.** `xcodebuild` refuses to run without Xcode's iOS platform components — several gigabytes of download. `swiftc` does not. `make typecheck` validates the AlarmKit and Vision code directly through the compiler, so the app layer could be written and checked against the iOS SDK while the platform download was still running. This is a small thing that saved the project days.

**The project file is generated, not committed as a source of truth.** `make project` regenerates `Desperta.xcodeproj` from `project.yml` via XcodeGen. Xcode project files are notoriously hostile to version control; generating it makes the configuration reviewable as plain YAML.

**Constraints documented as constraints.** The simulator cannot substitute for a device here — alarms, camera and Screen Time do not function in it. XcodeGen was built from source because the machine has no Homebrew. These are written down in the repository, because the next person to clone it (including me, in six months) will otherwise lose an afternoon rediscovering them.
