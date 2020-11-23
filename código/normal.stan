data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real musica_mu[n];
  real<lower=0> sigma[n];

  real playlist_mu;
  real<lower=0> playlist_sigma;
}
model {
  musicas ~ normal(musica_mu, sigma);
  musica_mu ~ normal(playlist_mu, playlist_sigma);
}