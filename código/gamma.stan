data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real<lower=0> playlist_alpha;
  real<lower=0> playlist_beta;
}
model {
  musicas ~ gamma(playlist_alpha, playlist_beta);
}
