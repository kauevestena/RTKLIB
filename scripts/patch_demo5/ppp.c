/* tropospheric model ---------------------------------------------------------*/
static int model_trop(gtime_t time, const double *pos, const double *azel,
                      const prcopt_t *opt, const double *x, double *dtdx,
                      const nav_t *nav, double *dtrp, double *var)
{
    static FILE *fp = NULL;           /* opened on first call, reused later  */
    double trp[3] = {0};
    char   tstr[32];

    /* ---------------------------------------------------------- */
    /* 1.  normal troposphere computation (unchanged)             */
    /* ---------------------------------------------------------- */
    if (opt->tropopt == TROPOPT_SAAS) {
        *dtrp = tropmodel(time, pos, azel, REL_HUMI);
        *var  = SQR(ERR_SAAS);
    }
    else if (opt->tropopt == TROPOPT_SBAS) {
        *dtrp = sbstropcorr(time, pos, azel, var);
    }
    else if (opt->tropopt == TROPOPT_EST || opt->tropopt == TROPOPT_ESTG) {
        matcpy(trp, x + IT(opt), opt->tropopt == TROPOPT_EST ? 1 : 3, 1);
        *dtrp = trop_model_prec(time, pos, azel, trp, dtdx, var);
    }
    else {
        return 0; /* unsupported mode */
    }

    /* ---------------------------------------------------------- */
    /* 2.  write one line of debug information                    */
    /* ---------------------------------------------------------- */
    if (!fp) {
        /* open once (append mode) – close at program exit automatically */
        fp = fopen("debug.csv", "a");
        if (!fp) return 1;            /* can’t log but don’t abort solver   */

        /* header line (optional) */
        fprintf(fp,
            "time,pos_x,pos_y,pos_z,az,el,ztd,grdN,grdE,"
            "dtdx0,dtdx1,dtdx2,delay,variance\n");
    }

    /* human-readable GPS-week time string, e.g. 2025/05/26 12:30:01.000 */
    time2str(time, tstr, 3);

    /* when gradients are not estimated, trp[1] and trp[2] stay zero      */
    fprintf(fp,
        "%s,%.3f,%.3f,%.3f,%.8f,%.8f,"          /* pos in m, angles in rad  */
        "%.6f,%.6f,%.6f,"                       /* troposphere states       */
        "%.6f,%.6f,%.6f,"                       /* dtdx[0..2]               */
        "%.6f,%.6f\n",                          /* slant delay, variance    */
        tstr, pos[0], pos[1], pos[2],
        azel[0], azel[1],
        trp[0], trp[1], trp[2],
        dtdx[0], dtdx[1], dtdx[2],
        *dtrp, *var);

    /* fflush(fp); */  /* uncomment if you want immediate disk write       */
    return 1;
}