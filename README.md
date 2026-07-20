# wycliffepeart

Moon-managed monorepo for Wycliffe Peart projects.

## Projects

- `apps/wp-profile` - GitHub profile content, static profile site, resume
  HTML/PDF workflow, deployment CLI, and Terraform infrastructure.

## Moon

List projects and tasks:

```sh
moon project wp-profile
```

Run `cliffe` through Moon from the monorepo root:

```sh
moon run wp-profile:cli-help
moon run wp-profile:resume-pdf
moon run wp-profile:init
moon run wp-profile:plan
moon run wp-profile:apply
moon run wp-profile:deploy
```

The profile app can still be used directly from `apps/wp-profile` with the
existing `cliffe` and Terraform commands documented in
`apps/wp-profile/docs.md`.
