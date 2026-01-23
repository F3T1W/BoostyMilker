class BoostyMilker < Formula
  include Language::Python::Virtualenv

  desc "CLI tool to download photos from Boosty"
  homepage "https://github.com/F3T1W/BoostyMilker"
  url "https://github.com/F3T1W/BoostyMilker/archive/refs/tags/v1.0.1.tar.gz"
  sha256 "528ee3f38943ad122b06d1eae2e6becd7798bf7fe1a425003bae006c820feb26"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/boosty-milker", "--help"
  end
end
