from __future__ import division
import re, os, random, argparse
from collections import OrderedDict, defaultdict

R = 3
M = 25

input_path = '../EC2Package'
result_path = 'sims_n=4536' # 216

os.system('rm -fr %s' % result_path)
os.mkdir(result_path)

aos_header = """LandisData  "Age-only Succession"

Timestep  10

SeedingAlgorithm  WardSeedDispersal

InitialCommunities      "../initial-communities.txt"
InitialCommunitiesMap   "../initial-communities.img"

EstablishProbabilities

>>>  mean values after preliminary survey
>> Species        Ecoregions
>> --------       ------------------
""".replace('\n', '\r\n')

# species -> ecoregion -> [min, max]
params = OrderedDict() # OD because we need to keep keys in order
header = [] # top part (i.e. non-table) of file

f = open('%s/EstablishProbabilities_PGInputs.csv' % input_path)
cols = f.readline().split(',')

for line in f:
    parts = line.split(',')
    values = dict(zip(cols, parts))
    species, ecoregion = values['species'], values['ecoregion']
    params.setdefault(species, OrderedDict())
    params[species][ecoregion] = [float(values[c]) for c in ['min', 'max', 'ccMin', 'ccMax']]
    assert params[species][ecoregion][0] <= params[species][ecoregion][1] and params[species][ecoregion][0] >= 0 and \
      params[species][ecoregion][0] <= 1 and params[species][ecoregion][1] >= 0 and params[species][ecoregion][1] <= 1
    assert params[species][ecoregion][2] <= params[species][ecoregion][3] and params[species][ecoregion][2] >= 0 and \
      params[species][ecoregion][2] <= 1 and params[species][ecoregion][3] >= 0 and params[species][ecoregion][3] <= 1

ecoregions = next(params.itervalues()).keys()

def copy_files(n, bf, bw, sp):
    os.system('cp %s/scenario.txt %s/%s/' % (input_path, result_path, n))
    os.system('cp %s/ExtractCohorts.r %s/%s/' % (input_path, result_path, n))
    os.system('cp %s/SimpleBatchFile.bat %s/%s/' % (input_path, result_path, n))
    os.system('cp %s/base-fire-6.0_%s.txt %s/%s/base-fire.txt' % (input_path, bf, result_path, n))
    os.system('cp %s/base-wind_%s.txt %s/%s/base-wind.txt' % (input_path, bw, result_path, n))
    os.system('cp %s/species%s.txt %s/%s/species.txt' % (input_path, sp, result_path, n))

n = 0

exp_map = []

for bf in ['hff-bs', 'hff-fs', 'lff-fs']:
    for bw in ['hs1000', 'hs500', 'ls500']:
        for sp in ['STol3', 'STol4', 'STol5']:

            # species -> ecoregion -> list of n samples (one in each bin)
            values = defaultdict(dict)

            for species in params:
                for ecoregion, vals in params[species].items():
                    size1 = (vals[1] - vals[0]) / M
                    samples1 = [str(round(random.uniform(vals[0] + size1 * i, vals[0] + size1 * (i + 1)), 2)) for i in range(M)]
                    size2 = (vals[3] - vals[2]) / M
                    samples2 = [str(round(random.uniform(vals[2] + size2 * i, vals[2] + size2 * (i + 1)), 2)) for i in range(M)]
                    assert all(float(v) >=0 for v in samples1)
                    assert all(float(v) >=0 for v in samples2)
                    #print species, ecoregion, vals, samples
                    random.shuffle(samples1)
                    random.shuffle(samples2)
                    values[species][ecoregion] = [samples1, samples2]
                    #print '------'

            for r in range(R):
                for cc_idx in [0, 1]:
                    for m in range(M):
                        os.mkdir('%s/%s' % (result_path, n))
                        fout = open('%s/%s/age-only-succession.txt' % (result_path, n), 'w')
                        fout.write(aos_header)
                        fout.write('\t'.join([''] + ecoregions) + '\r\n')
                        for species in params.keys():
                            row = [species] + [values[species][er][cc_idx][m] for er in ecoregions]
                            fout.write('\t'.join(row) + '\r\n')
                        fout.close()
                        copy_files(n, bf, bw, sp)
                        exp_map.append([n, bf, bw, sp, m, cc_idx, r])
                        n += 1

                for aos_special in ['maxCC', 'max', 'meanCC', 'mean', 'minCC', 'min']:
                    os.mkdir('%s/%s' % (result_path, n))
                    os.system('cp %s/age-only-succession_%s.txt %s/%s/age-only-succession.txt' % (input_path, aos_special, result_path, n))
                    copy_files(n, bf, bw, sp)
                    cc_idx = 1 if 'CC' in aos_special else 0
                    exp_map.append([n, bf, bw, sp, aos_special, cc_idx, r])
                    n += 1

f = open('%s_infos.csv' % result_path, 'w')
f.write(','.join(['i', 'base-fire', 'base-wind', 'species', 'm', 'cc', 'r']) + '\r\n')
for row in exp_map:
    f.write(','.join([str(v) for v in row]) + '\r\n')
f.close()

print n
