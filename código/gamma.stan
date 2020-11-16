data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real<lower=0, upper=1> alpha0;
  real<lower=0, upper=1> beta0;
}
model {
  musicas ~ gamma(alpha0, beta0);
}
