MAX_TRANSCRIPTS = pow(26, 3)

transcripts_range = range(65, 91)


def generate_transcripts(count):
    if count > MAX_TRANSCRIPTS:
        raise AssertionError(f'too many transcripts: {count}')
    tcs = []
    for i in transcripts_range:
        for j in transcripts_range:
            for k in transcripts_range:
                tcs.append(f'{i:c}{j:c}{k:c}')
                if len(tcs) == count:
                    return tcs
