data {
  int<lower=0> n;
  int<lower=0> m;
  int uns_zeros[3,n];
  vector[m] musicas;
}
parameters {  
  simplex[3] theta;
  real<lower=0> alpha;
  real<lower=0> beta;
}
model {
  for (i in 1:n)
    uns_zeros[,i] ~ multinomial(theta);

  musicas ~ beta(alpha, beta);
}
