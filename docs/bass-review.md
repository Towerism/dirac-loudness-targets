# What independent reviews found about the bass

If preset 3 sounds boomy, first check that you aren't listening louder than it is designed for. Then give your ears a few weeks before changing the curves. The steps are under [If preset 3 still sounds boomy](#if-preset-3-still-sounds-boomy).

Four AI reviews checked the bass. Each was given only the curve files and the facts about the system, and none was told how the curves sounded to the owner. They agree that the deep-bass amount follows ISO 226, the standard for how loudness perception changes with volume. They disagree about how far up into the upper bass the lift should reach.

## What every review agreed on

- **A target curve can't make bass ring for a shorter or longer time.** That depends on the room and on Dirac Live ART (Active Room Treatment, which makes the speakers work together to cut room ringing). How smoothly the subwoofers hand over to the main speakers also plays a part. Dirac says ART works from 20 to 150 Hz and reduces decay time there ([ART FAQ](https://helpdesk.dirac.com/en/dirac-art/Dirac-Live-Active-Room-Treatment-ART-FAQ-9be7)). A target curve sets how loud each part of the bass is next to the midrange.
- **From 40 to 100 Hz the bass lift matches ISO 226 within about 0.6 dB.** Below 40 Hz the lift stops rising, so at 20 Hz preset 3 gives about 2 dB less than ISO 226 asks for. At their intended levels, presets 2 and 3 should sound about as full from 40 to 100 Hz as preset 1 does at reference.
- **How far up the lift reaches matters most between about 125 and 400 Hz.** An earlier version carried the lift up to about 400 Hz in preset 3, and one ended it at 250 to 350 Hz. They differed by up to about 2 dB in that range. ART doesn't act above 150 Hz. There, the difference changes how loud the upper bass is, and it doesn't change how long bass rings.

## Where the reviews split

They disagreed about how far up the bass lift should reach.

- **Ending it low,** at 250 to 350 Hz, keeps voices clean. A Bose patent says that the loudness controls of its time "cause voices to be perceived as very bass heavy (boomy) when reproduced at low volume levels", because people expect quiet voices to have little bass. Its claims cover a boost that is negligible above 100 Hz for volume cuts under 20 dB, and above 200 Hz for cuts of 20 to 40 dB ([US4490843](https://patents.google.com/patent/US4490843A/en)). Preset 3 is meant for a cut of about 20 dB, where those two limits meet. The cost of ending low is that 150 to 300 Hz may sound lean, and the deep bass may sound like a separate layer under the rest.
- **Carrying it higher** follows ISO 226 more closely and sounds fuller and warmer. The risk is that male voices sound thick, and that any extra upper bass the room adds between 150 and 300 Hz gets louder.
- **One review suggested a shape between the two** for preset 3, with the lift falling to half by about 160 Hz and almost gone by 400 Hz.

They also split on the Subwoofer curve. In StormAudio's original, it stays near +4 dB from 100 Hz to its 140 Hz correction limit while LCR falls, so it sits up to 2.8 dB above LCR near the crossover. Some reviews suggested making it follow LCR there. Others pointed out that if Dirac builds the shared bass target from the Subwoofer file, that would remove up to 2.8 dB of upper bass, and Dirac doesn't document which file it uses.

## The baseline the curves use now

A final review was given the five reports, the candidate versions and the owner's design preferences, without the owner's listening impressions or the order in which versions were made. It chose:

- **A bass fade that falls to zero at 400 Hz in both packages** (`f1=55, f2=400` in `tools/build.py`). The lift stays within about 0.7 dB of ISO 226 up to 125 Hz, falls to half near 150 Hz, where ART stops working, and adds less than ISO 226 from there up, where voices sit.
- **StormAudio's original Subwoofer curve.** Whether aligning it helps depends on how Dirac uses the file, so the vendor's file stays as it was.
- **The bass amount, treble shelf and presence dip as they were.**

## Why the amount may feel unfamiliar

Two reviews called the amount right for film. One called it generous for TV and streaming, which are mixed louder than film, and so for most late-night viewing. One added that listening 5 dB above a preset's intended level moves the balance at 40 Hz by about 2 dB.

ISO 226 predicts how much bass keeps the balance the same at a lower volume. In a headphone test with real music, listeners set a bass boost until the quiet version sounded like the louder one, and their median setting came out "near 0 dB" from the prediction ([Fierro, Rämö and Välimäki, 2019](https://zenodo.org/records/3249289)). On one track that held almost nothing but bass and drums, most listeners set more boost than predicted. The authors put this down to the task being harder with nothing outside the bass to compare against. The test shows that the prediction matches what listeners hear on average. It doesn't measure which balance a given listener enjoys.

Before these curves, the owner had used Harman-style curves (target curves from Harman's research that slope gently up into the bass) with a +6 dB or +10 dB bass lift, for over a year, at 10 to 20 dB below reference. The table subtracts what ISO 226 says the ear needs at each level from each curve's lift. Here, "reference-level balance" means a curve with no bass lift. StormAudio's curve, and so every preset in this repo, already lifts 50 Hz by about 4.8 dB, which is the last row.

| Setup | Bass at 50 Hz relative to reference-level balance |
|---|---|
| +6 dB lift at −10 dB | about +1.9 dB |
| +10 dB lift at −10 dB | about +5.9 dB |
| +6 dB lift at −20 dB | about −2.2 dB |
| +10 dB lift at −20 dB | about +1.8 dB |
| Presets 2 and 3 in this repo, at their intended levels | about +4.8 dB |

At −20 dB the owner had been hearing about 3 to 7 dB less bass than preset 3 gives. At −10 dB, the +10 dB curve gave about 1 dB more than the presets do. Part of the boominess at −20 dB may be this change in what the owner was used to. The owner decided to treat the boominess as habit for now.

## If preset 3 still sounds boomy

Try these one at a time. Compare each with the current preset 3 at a matched level.

1. **Check the playback level.** Set the volume where you usually listen on preset 3. Play pink noise limited to 500 Hz to 1 kHz, and measure at your seat with an SPL meter set to C-weighting. Do the same on preset 1 with the volume at 0. Preset 3 should read about 20 dB lower. If the gap is smaller, you are listening louder than preset 3 is designed for.
2. **Lower the bass lift.** In `tools/build.py`, change package 3's `gb` from 8.3 to about 5. That gives about 1.5 dB of bass over a reference-level balance at −20 dB, close to the 1.8 dB the old +10 dB curve gave. Run `make build`. In `tools/check.py`, set package 3's `GB` and its 31 and 50 Hz values to the new `gb`, then run `make check`. Preset 3 now needs +5 on the volume dial at reference, where it needed +8.5.
3. **End the bass lift lower.** If male voices sound thick on preset 3, set package 3's `f2` back to 350 Hz. This also changes the expected values at 100, 140 and 200 Hz in `tools/check.py`. The README's section on rebuilding explains how to work them out.

`git checkout tools/build.py tools/check.py targets/` undoes these changes.

## Not checked yet

- Measurements of each preset at its intended level with Room EQ Wizard (REW), a free measurement program, including how long the bass rings between 40 and 200 Hz. If the ringing is the same in every preset, any difference you hear comes from the tonal balance.
- Whether Dirac builds the shared bass target from the Subwoofer file. If 100 to 140 Hz sounds hollow or heavy, try making the Subwoofer curve in `stormaudio-based` follow LCR from 100 Hz to its 140 Hz limit.
- Dirac's predicted response, checked for large boosts below each speaker's natural roll-off. The main speaker curves allow correction down to 1 Hz, so Dirac may try to boost bass that those speakers can't play.
