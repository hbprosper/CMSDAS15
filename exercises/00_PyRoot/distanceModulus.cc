//-----------------------------------------------------------------------------
// File: distanceModulus
// Description: Fit Lambda CDM model to a compilation of Type Ia 
//              supernova data.
//
//              a    - universal scale factor
//
//              OM   - Omega_M
//              OL   - Omega_Lambda
//              H    - related to Hubble's constant
//
// Created: June 2008 HBP
// Updated for ESHEP 2012, La Pommeraye, Anjou, France
//-----------------------------------------------------------------------------
#include <cmath>
#include <cassert>
#include <iostream>
using namespace std;
//-----------------------------------------------------------------------------
double OFFSET=5*log10(2.99*pow(10.0, 5.0))+25;
//-----------------------------------------------------------------------------

// Lambda CDM model
double lambdaModel(double a, double OM, double OL)
{
  // a^3 * [Omega_M/a^3 + (1-Omega_M-Omega_L)/a^2 + Omega_L]
  double y = OM + (1 - OM - OL)*a + OL*a*a*a;
  if ( y > 0 )
    return y;
  else
    return 1.e50;
}

// random phantom energy model
double phantomModel(double a, double OM, double OL)
{
  return exp(OM*a+OL*a*a);
}


// pick model
double (*model)(double, double, double) = lambdaModel;

// compute distance modulus
double distanceModulus(double z, double OM, double OL, double H)
{
  int N=200;
  double F = 0;
  double a = 1.0/(1+z);
  double h = (1-a) / N;
  
  for(int i=0; i < N; i++)
    {
      double x = a + (i+0.5)*h;
      F = F + 1.0/sqrt(x * model(x, OM, OL));
    }

  F = F*h;
  double OK = 1 - OM - OL;

  if ( OK != 0 )
    {      
      double rootOK = sqrt(fabs(OK));
      double theta  = rootOK * F;
      if ( OK > 0 )
        F = sinh(theta);
      else
        F = sin(theta);
      F /= rootOK;
    }

  double y = 5*log10((1+z)*F/H) + OFFSET;
  return y;
}


