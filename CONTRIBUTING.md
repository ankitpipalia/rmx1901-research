# Contributing

This repository is primarily a research record. Corrections, reproductions,
and clearly sourced counter-evidence are welcome.

## Good contributions

- A factual correction with a citation to a public source, a vendor
  advisory, or a reproducible measurement.
- An independent reproduction of a stated result, including the exact
  build, kernel, and tool versions.
- A clarification that separates a measured result from an inference.
- A sanitized test fixture or an offline unit test that improves the tools.

## Please do not

- Open an issue or PR containing IMEI, MEID, serial numbers, MAC addresses,
  account data, tokens, NV/persist dumps, firmware, APKs, or proprietary
  binaries.
- Ask for a working unlock, a signed programmer, a vendor token, or a
  one-click root package. Those are out of scope and will not be provided.
- Submit third-party code without its license and attribution.
- Present an inference as a measurement.

## Style

- Markdown, one sentence per line is not required; keep paragraphs readable.
- Use tables for matrices and claim/evidence summaries.
- State the build and kernel for any device result.
- Use `measured`, `derived`, or `inferred` explicitly when the distinction
  matters.
- Sanitize commands: replace serials with `<serial>`, ports with `<port>`,
  paths with `<home>`, and network addresses with `<host>`.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests are offline and use synthetic fixtures. No device is required.

## Licensing

By contributing code you agree that it is licensed under the MIT License.
By contributing documentation you agree that it is licensed under CC BY 4.0.
