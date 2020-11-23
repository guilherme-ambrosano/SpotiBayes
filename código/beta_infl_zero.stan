data {
  int<lower=0> n;
  int<lower=0> m;
  int uns_zeros[3,n];
  vector[m] musicas;
}
parameters {
  real<lower=0, upper=1> musica_alpha[m];
  real<lower=0, upper=1> musica_beta[m];
  
  simplex[3] playlist_theta;
  real<lower=0, upper=1> playlist_alpha;
  real<lower=0, upper=1> playlist_beta;
}
transformed parameters {
  real medias[m];
  for (i in 1:m) {
    medias[i] = musica_alpha[i]/(musica_alpha[i] + musica_beta[i]);
  }
}
model {
  for (i in 1:n)
    uns_zeros[,i] ~ multinomial(playlist_theta);

  musicas ~ beta(musica_alpha, musica_beta);
  medias ~ beta(playlist_alpha, playlist_beta);
}
