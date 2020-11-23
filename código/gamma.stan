data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real<lower=0, upper=1> musica_alpha[n];
  real<lower=0, upper=1> musica_beta[n];

  real<lower=0, upper=1> playlist_alpha;
  real<lower=0, upper=1> playlist_beta;
}
transformed parameters {
  real medias[n];
  for (i in 1:n) {
    medias[i] = musica_alpha[i]/musica_beta[i];
  }
}
model {
  musicas ~ gamma(musica_alpha, musica_beta);
  medias ~ gamma(playlist_alpha, playlist_beta);
}
