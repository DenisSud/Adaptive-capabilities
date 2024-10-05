FROM rust:1.70-slim-bullseye as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libclang-dev \
    cmake \
    libopencv-dev \
    clang \
    gcc \
    g++ \
    make \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install latest CMake
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.sh \
    -q -O /tmp/cmake-install.sh \
    && chmod u+x /tmp/cmake-install.sh \
    && mkdir /opt/cmake \
    && /tmp/cmake-install.sh --skip-license --prefix=/opt/cmake \
    && rm /tmp/cmake-install.sh \
    && ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake

# Set up the Rust toolchain
RUN rustup component add rustfmt
RUN rustup component add clippy
RUN rustup component add rust-src

# Set up environment variables
ENV RUST_BACKTRACE=1
ENV OPENCV_LINK_LIBS=opencv_core,opencv_imgproc,opencv_imgcodecs
ENV OPENCV_LINK_PATHS=/usr/lib/x86_64-linux-gnu
ENV LIBCLANG_PATH=/usr/lib/llvm-11/lib

# Set the working directory
WORKDIR /app

# Start a shell by default
CMD ["/bin/bash"]
