readonly EIF_PATH="/app/simple-ne-server.eif"

# Enclaves running on x86 instances must have whole numbers of vCPUs, in multiples of 2, since whole cores (not hyperthreads) are sliced off and dedicated to the enclave, for security.
# The minimum core count is 2. The following error appears to be about memory, but is actually due to 1 core being specified instead of 2.
readonly ENCLAVE_CPU_COUNT=2
readonly ENCLAVE_MEMORY_SIZE=5000

main() {
    nitro-cli run-enclave --cpu-count $ENCLAVE_CPU_COUNT --memory $ENCLAVE_MEMORY_SIZE \
        --eif-path $EIF_PATH --debug-mode --enclave-cid 99999

    vsock-proxy 8000 kms.us-east-1.amazonaws.com 443 &

    local enclave_id=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
    echo "-------------------------------"
    echo "Enclave ID is $enclave_id"
    echo "-------------------------------"

    nitro-cli console --enclave-id $enclave_id # blocking call.
}

main