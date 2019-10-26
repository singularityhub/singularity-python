# Changes

 - [build.go](build.go) is from [here](https://github.com/sylabs/singularity/blob/release-3.4/internal/pkg/build/build.go)
 - [bundle.go](bundle.go) is from [here](https://github.com/sylabs/singularity/blob/release-3.4/pkg/build/types/bundle.go)

For bundle.go, we accept an extra argument for the stage, and the directory
created is named based on that. Build.go then provides this stage. If no stage
is provided, it works as normal.
