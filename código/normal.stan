data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real playlist_mu;
  real<lower=0> playlist_sigma;
}
model {
  musicas ~ normal(playlist_mu, playlist_sigma);
}