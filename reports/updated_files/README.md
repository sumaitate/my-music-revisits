# Complete-file delivery

Use final_updated_files.zip for the integrated final version. It contains complete source files, tests, packaging, README, the updated EDA notebook source, and the audit/evaluation/changelog reports. It is not a diff. The raw export and regenerated parquet files remain in the project workspace; rebuild them using the README commands.

manifest.json lists removed paths and SHA-256 digests. When applying the archive over an older copy, remove the listed obsolete paths as well.

phase1.zip and phase2.zip are saved intermediate source checkpoints. phase3.zip through phase5.zip are cumulative complete-file delivery bundles assembled after integration. The final archive supersedes intermediate bundles.
