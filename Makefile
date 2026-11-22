RUN := uv run --quiet

.PHONY: build check selftest plot

# Rebuild both quieter packages from targets/stormaudio-based.
build:
	$(RUN) tools/build.py targets/stormaudio-based targets

# Check the built packages. Prints only failures, and exits 1 if there are any.
check:
	$(RUN) tools/check.py targets/stormaudio-based targets -v

# Prove the checker can fail: unmodified copies of the source must be rejected.
selftest:
	rm -rf build/selftest && mkdir -p build/selftest
	cp -r targets/stormaudio-based build/selftest/stormaudio-minus10dB
	cp -r targets/stormaudio-based build/selftest/stormaudio-minus20dB
	! $(RUN) tools/check.py targets/stormaudio-based build/selftest > /dev/null
	@echo "selftest ok: the checker rejects an unmodified package"

# Redraw docs/curves.png (LCR) and docs/subwoofer.png.
plot:
	$(RUN) tools/plot.py targets docs/curves.png
	$(RUN) tools/plot.py targets docs/subwoofer.png "Subwoofer Cinema StormAudio.targetcurve"
