# Runtime Deploy

## Product deployment shape
Deploy the repository as:
- one unified skill entry: `skills/long-chain-autonomy/`
- retained atomic skills under `skills/`
- runtime scripts under `scripts/`
- runtime state/audit directories under `.agent/`
- packaged skills under `dist/`

## Fast deploy checklist
- mainline checks exist
- risk policy exists
- resume scripts exist
- heartbeat / observability scripts exist
- handoff / inheritance state exists
- release manifest exists

## Repository role
- `wlcc-release` is the formal deployable git repository
- the unified skill is the top entry surface
- runtime infrastructure remains the execution substrate
