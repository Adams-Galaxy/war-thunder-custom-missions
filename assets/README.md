# Reusable assets

This directory catalogs reusable weapons, vehicle integrations, and tuning
profiles separately from complete missions. It is intentionally data-first so a
future Python builder can read manifests and generate War Thunder BLK files
without changing the stable mission URLs or hand-maintained source assets.

## Weapon catalog

| Asset | Manifest | Current platform | Status |
| --- | --- | --- | --- |
| SCALP-EG gameplay proxy | [`weapons/scalp-eg/asset.toml`](weapons/scalp-eg/asset.toml) | Rafale M F3-R | Three single-player variants |

The installable files referenced by each manifest remain under the relevant
experiment's `content/pkg_local` directory. That directory mirrors War
Thunder's required on-disk structure and is the canonical source; the asset
catalog does not duplicate BLK definitions.
