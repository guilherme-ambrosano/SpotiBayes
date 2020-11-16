data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real mu0;
  real<lower=0> sigma0;
}
model {
  musicas ~ normal(mu0, sigma0);
}