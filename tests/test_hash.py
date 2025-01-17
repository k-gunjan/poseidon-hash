import pytest as pytest

import poseidon

# using https://extgit.iaik.tugraz.at/krypto/hadeshash/-/tree/master/code
# WARNING. Fix bug with matrix multiplication in code above (see them README). Use Output[1] for tests
# sage poseidonperm_x5_254_3.sage
output_254 = "0x1357e867b0efbd9d865420117785ee2c9360745c7c5b4bc11782be67e6cb0b59"
# sage poseidonperm_x5_255_5.sage
output_255 = "0x4415f84efb53753a723c8a57fc8a56038b88471d4bb32fb8d82240289fd0a33d"


# Compare with reference implementation https://extgit.iaik.tugraz.at/krypto/hadeshash
@pytest.mark.parametrize("t ,full_round, partial_round, alpha, prime, input_rate, security_level, rc, mds, output", [
    (3, 8, 57, 5, poseidon.prime_254, 2, 128, poseidon.round_constants_254, poseidon.matrix_254,
     output_254),
    (5, 8, 60, 5, poseidon.prime_255, 4, 128, poseidon.round_constants_255, poseidon.matrix_255,
     output_255),
])
def test_not_optimized_poseidon(t, full_round, partial_round, alpha, prime, input_rate, security_level, rc, mds,
                                output):
    instance = poseidon.Poseidon(prime, security_level, alpha, input_rate, t=t, full_round=full_round,
                                 partial_round=partial_round, rc_list=rc, mds_matrix=mds)
    input_vec = [x for x in range(0, t)]
    actual = instance.run_hash(input_vec)
    assert int(output, 16) == int(actual)


@pytest.mark.parametrize("hash_type, t ,full_round, partial_round, alpha, prime, input_rate, security_level, rc, mds", [
    (poseidon.HashType.CONSTINPUTLEN, 4, 8, 56, 5, poseidon.prime_255, 3, 128, poseidon.round_constants_neptune,
     poseidon.matrix_neptune),
])
def test_optimized_poseidon(hash_type, t, full_round, partial_round, alpha, prime, input_rate, security_level, rc, mds):
    instance_optimized = poseidon.OptimizedPoseidon(hash_type, prime, security_level, alpha, input_rate, t=t,
                                                    full_round=full_round, partial_round=partial_round, rc_list=rc,
                                                    mds_matrix=mds)
    instance_non_optimized = poseidon.Poseidon(prime, security_level, alpha, input_rate, t=t, full_round=full_round,
                                               partial_round=partial_round, rc_list=rc, mds_matrix=mds)
    input_vec = [x for x in range(0, t - 1)]
    domain_tag = (t - 1) * (2 ** 64)
    input_vec_opt = [domain_tag, *input_vec]
    actual_optimized = instance_optimized.run_hash(input_vec)
    actual_non_optimized = instance_non_optimized.run_hash(input_vec_opt)

    assert actual_optimized == actual_non_optimized
