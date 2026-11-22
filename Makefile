RUN := uv run --quiet
PACKAGES := stormaudio-minus5dB stormaudio-minus10dB stormaudio-minus20dB  # the packages tools/build.py makes

.PHONY: build check selftest plot

# Rebuild the quieter packages from targets/stormaudio-based.
build:
	$(RUN) tools/build.py targets/stormaudio-based targets

# Check the built packages. Prints only failures, and exits 1 if there are any.
check:
	$(RUN) tools/check.py targets/stormaudio-based targets -v

# Prove the checker can fail: unmodified copies of the source must be rejected.
selftest:
	rm -rf build/selftest && mkdir -p build/selftest
	for p in $(PACKAGES); do cp -r targets/stormaudio-based build/selftest/$$p; done
	! $(RUN) tools/check.py targets/stormaudio-based build/selftest > build/selftest/out.txt
	# Each package must fail on its own, so a package missing from the checker can't pass unnoticed.
	for p in $(PACKAGES); do grep -q "AC3 $$p/" build/selftest/out.txt || exit 1; done
	@echo "selftest ok: the checker rejects an unmodified package"

# Redraw docs/curves.png (LCR) and docs/subwoofer.png.
plot:
	$(RUN) tools/plot.py targets docs/curves.png
	$(RUN) tools/plot.py targets docs/subwoofer.png "Subwoofer Cinema StormAudio.targetcurve"
