data {
  int<lower=0> n;
  int<lower=0> m;
  int uns_zeros[3,n];
  vector[m] musicas;
}
parameters {
  simplex[3] theta0;
  real<lower=0, upper=1> alpha0;
  real<lower=0, upper=1> beta0;
}
model {
  for (i in 1:n)
    uns_zeros[,i] ~ multinomial(theta0);

  musicas ~ beta(alpha0, beta0);
}
