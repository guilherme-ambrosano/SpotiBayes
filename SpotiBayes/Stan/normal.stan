data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  musicas ~ normal(mu, sigma);
}