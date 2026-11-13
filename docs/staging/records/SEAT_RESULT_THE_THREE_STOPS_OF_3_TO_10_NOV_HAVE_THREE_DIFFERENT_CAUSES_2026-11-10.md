**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted`

# The three stops of 3-10 Nov have three different causes, and the off-box dead-man missed the third (2026-11-10)

**Work id:** `off-box-liveness-workflow` (director's yes, 8 Nov; due 15 Nov). **Evidence read on 10 Nov, 21:00-21:30Z:**
- the guest journal (`journalctl --list-boots`, boots -3 to 0);
- the Windows System and Application event logs, read from the guest through interop (`powershell.exe Get-WinEvent`);
- WSL's crash folder on the host (`%LOCALAPPDATA%\Temp\wsl-crashes`);
- the ops repo's Actions run history (`gh run list`, `gh api .../jobs`);
- the ops heartbeat's commit history.

So the Windows side **was** readable from the guest, and the director's host was not needed for any of the three.

## The causes

| Stop | Cause | Confidence |
|---|---|---|
| **3-4 Nov** (~23h: 3 Nov 09:15 to 4 Nov ~08:20) | **The interactive Claude Code login expired.** The box was up and landed nothing. This was a stall, not a machine stop. Windows' daily uptime event (6013) shows no host reboot. | Established. These are the director's words of 4 Nov 08:22 ("I needed to login and authorise again"), `advisor/done/DIRECTOR_STEER_USE_THE_LONG_LIVED_TOKEN_...2026-11-04.md`. It is fixed by the one-year token. |
| **5-7 Nov** (~60h: 5 Nov 03:31:52Z to 7 Nov 15:24Z) | **A WSL2 guest kernel panic.** The host file `wsl-crashes\kernel-panic-1793849512-{05b710e0-...}.txt` is stamped 03:31:52Z. It reads: `int3` in `memcpy`, from `p9_read_work → __vsock_connectible_recvmsg → hvs_stream_dequeue → __hv_pkt_iter_next`, then "Kernel panic - not syncing: Fatal exception in interrupt", kernel `6.6.114.1-microsoft-standard-WSL2`. That is a fault in the kernel's 9p file-sharing read over the Hyper-V socket (the path that serves Windows-side files and interop). It is not memory: the only OOM line in the dump is ~13.8h older, a 0.5 GB cgroup kill. Windows stayed up throughout (6013 at 12:00 on 5, 6 and 7 Nov), and **nothing relaunched the guest for 60h** because the only relauncher was the boot-triggered keeper. | Established for the panic and its call path. *Why* that path faulted (a kernel bug, or what was reading through 9p at 03:31) we cannot tell. |
| ↳ 7 Nov 14:56 / 15:43 | Separately, the **host** shut down uncleanly at 14:56:09 (Event 6008, then Kernel-Power 41 at boot, with no bugcheck). It was woken by keyboard or mouse input at 15:21 (Kernel-Power 566, `InputHid`) and booted 15:24. The guest's short boot -2 then ended at 15:43 because **Windows Update restarted the PC** (Event 1074, `MoNotificationUx.exe`, "Service pack (Planned)"). Neither caused the 60h; the guest had been dead since 5 Nov. | Established from the event log. Why the host went down at 14:56 (power, a hang) we cannot tell: no bugcheck was written. |
| **10 Nov** (~10h: 08:26:45 to 18:33Z) | **Windows Update auto-installed WSL 3.0.5.0, and its installer stopped WSL.** Event 43 at 08:26:17 ("Windows Subsystem for Linux 3.0.5.0"). At 08:26:41 Restart Manager closed `wsl.exe`, `wslhost.exe`, `vmwp.exe` and the rest, and logged each "cannot be restarted". The guest's orderly systemd poweroff followed at 08:26:45, and the install completed at 08:27:51. Nothing restarted WSL until the PC was woken at 18:32 (Kernel-Power 566). The new package brought kernel `6.18.58.1`, which is what runs now. | Established. |

**The LiveKernelEvent 193 / WATCHDOG reports are not a cause.** They appear every ~4h from 3 to 10 Nov, including near 04:28 on 5 Nov and 08:23 on 10 Nov, which makes them look relevant. Every one of them attaches the same dump, `WATCHDOG-20261015-0930.dmp`: Windows Error Reporting is re-queuing one 15 Oct report.

## Corrections beside earlier claims

- `staging/done/SEAT_NOTE_OFF_BOX_LIVENESS_WORKFLOW_DRAWN_TWICE_DISPOSITION_2026-11-08.md` said "the host stopped the WSL VM at 03:31:52Z ... who stopped it, we cannot tell". **Wrong:** nothing on the host stopped it. The guest kernel panicked, and 03:31:52Z is the panic file's timestamp.
- `docs/design/HOST_AUTOSTART_TOPOLOGY.md` (the 10 Nov section) said "the keeper had exited before WSL stopped ... and WSL then shut down when the director's last terminal window closed". **Wrong:** WSL was stopped by the WSL 3.0.5.0 installer. The receipt is written only when a keeper *starts*, so a last line of 7 Nov 15:47 is what a keeper alive since 7 Nov would also leave; it cannot show an exit. Corrected in that file in this commit. The director's fix there (the 5-minute repeating trigger) is the right one for both the 5 Nov and 10 Nov shapes: either way WSL comes back within 5 minutes while Windows is up.

## A defect in the off-box workflow: it missed the 10 Nov stop

The workflow is on the ops repo (`2b628fed8`, 8 Nov). Its decider passes 6 tests, including the stale-heartbeat test. A forced-stale run on GitHub decided `dead` (run 42488445238, 8 Nov). **It still did not tell the director about 10 Nov:**
- The ops heartbeat went quiet from 08:01:43Z to 18:47:37Z, a 10.8h gap.
- GitHub delivered the hourly `"23 * * * *"` schedule only **8 times in about 54 hours**: 8 Nov 18:53 and 22:57; 9 Nov 02:45, 11:50 and 22:31; 10 Nov 04:41, 13:37 and 20:54. The gaps run from 3.8h to 10.7h.
- The only run inside the stop, at 13:37Z, saw a heartbeat 5.6h old (under the 6h threshold) and correctly stayed silent. The next run, at 20:54, came after the box was back.

So what the workflow can catch is the threshold plus the gap between delivered runs, which is up to about 17h, not 6h.

**Fix landed on the ops repo:** the schedule is now `"7,37 * * * *"`. If every run fires, that caps at about 1,440 billed minutes a month. This is the account's only private-repo workflow (`geo-monitor` has had 0 runs in 30 days), so the cap sits inside the free quota and spends no money.

### Pre-registration (written before any run under the new schedule)

- **Prediction:** over the 72h after the ops push, GitHub delivers at least 2x the old rate (≥ 0.3 runs/h, against 0.15/h), and the longest gap between delivered scheduled runs is **under 6h**.
- **Refutation:** fewer than 0.3 runs/h, or any gap ≥ 6h. Either one means a denser cron does not buy delivery. The next move would then be a trigger that does not depend on GitHub's scheduler, for example the advisor's cloud routine calling `workflow_dispatch`, and that would come to the director as a proposal.
- **Check:** `gh run list -R 21bcarlisle-arch/synthetic-enterprise-ops --workflow off-box-deadman.yml --event schedule -L 200`, on or after 13 Nov 22:00Z.

## What would tell next time, where we still cannot tell

- **Why the 9p path panicked:** the panic file is the whole record. A repeat on kernel 6.18 would point to a live bug, worth reporting to microsoft/WSL with the file attached. No repeat suggests it was fixed in the new kernel. The crash folder keeps the file, so watch it (`ls %LOCALAPPDATA%\Temp\wsl-crashes`).
- **Why the host went down at 14:56 on 7 Nov:** with no bugcheck, only the director can say whether there was a power cut or he found the PC hung.
- **The WSL auto-update will recur.** The 5-minute trigger bounds it to about 5 minutes while Windows is up. Pausing WSL's Store/Windows Update channel would remove it, but that is a host security-posture choice (G5), so it is not made here.

## Done-means, against the commitment

Workflow on the ops repo: yes. Its stale-heartbeat test green: yes, 6 passed, and it decided `dead` on GitHub. Credential only in repo secrets: yes, `NTFY_TOPIC`, set 8 Nov 14:09Z. Each stop has a cause: yes, all three above.

Still open: the send leg has never run live (the 8 Nov note recommends no test push), and the cadence prediction above is still to be checked.

## Result of the pre-registration (checked 13 Nov 22:05Z): REFUTED on both legs

The `"7,37 * * * *"` cron reached the ops remote at 10 Nov 21:10:49Z as 199bf3f32, so the 72h window is 10 Nov 21:10 to 13 Nov 21:10. The ops-push outage of 10 to 13 Nov did not delay it: that outage was *caused* by this commit sitting on the remote.

| | runs | hours | rate | gaps between delivered runs (h) | longest |
|---|---|---|---|---|---|
| before, `23 * * * *` (8 Nov 18:53 to the push) | 8 | 50.3 | 0.159/h | 4.1, 3.8, 9.1, 10.7, 6.2, 8.9, 7.3 | 10.7 |
| after, `7,37 * * * *` (72h window) | 10 | 72.0 | **0.139/h** | 4.6, 6.9, 8.2, 6.4, 4.8, 8.8, 7.8, 5.0, 7.3, 8.4 | **8.8** |

The prediction was at least 0.3 runs/h with every gap under 6h. Measured: 0.139/h, and 7 of 10 gaps were 6h or longer. Twice as many cron entries bought no extra delivery: GitHub ran this workflow about every 4 to 9 hours under either schedule. All 18 runs concluded `success`. So the scheduler, not the workflow, is what limits it.

**What this means for the dead-man.** A stop is detected after the 6h staleness threshold plus the wait for the next delivered run. At the measured worst gap, that is about 15h. The guarantee is "about 15h", not "about 7h".

**Next move, as pre-registered:** a trigger that does not depend on GitHub's scheduler, for example the advisor's cloud routine calling `workflow_dispatch`. Creating a Routine is console-only, so this goes to the director as a proposal in `for_the_director`. Until he rules, the 30-minute cron stays: it costs nothing over the hourly one and is no worse.

**Reverse.** Delete this file, revert the `HOST_AUTOSTART_TOPOLOGY.md` paragraph, and set the ops cron back to `"23 * * * *"`.
