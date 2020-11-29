data {
  int<lower=0> n;
  vector[n] musicas;
}
parameters {
  real<lower=0> alpha;
  real<lower=0> beta;
}
model {
  musicas ~ gamma(alpha, beta);
}
